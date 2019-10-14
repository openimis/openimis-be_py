# GraphQL interface to openIMIS

GraphQL allows openIMIS to provide a single interface to manipulate data across modules transparently.
This document provides a quick introduction at the way to query this API.

When running in development mode, accessing the `/graphql` endpoint on the backend server will provide
a useful interface to query the API, browse the documentation and explore the data structures.

## Client-side

### Basic queries

Our very first query will ask for a list of claims:
```
{
    claims {
        edges {
            node {
                id
            }
        }
    }
}
```

The top `claims` is a query. They will usually use the name of the resource they're exposing. A
singular name will be used to query a specific claim while the plural will provide a list.
This query will return something like:

```
{
  "data": {
    "claims": {
      "edges": [
        {
          "node": {
            "id": "Q2xhaW1HUUxUeXBlOjE="
          }
        },
        {
          "node": {
            "id": "Q2xhaW1HUUxUeXBlOjI="
          }
        },
(...)
```

The `data` section contains the actual results. `claims` is the name of our query.
When

To query a specific claim:
```
{
  claim(id: 2) {
    id
  }  
}
```

To put more than one query at once and avoid name conflicts in the results, one can "alias"
a query. Here we are naming it "test".

```
{
  test: claimAdmins(lastName_Icontains:"L") {
    edges {
      node {
        id
        lastName
        otherNames
        code
      }
    }
  }
  claims(first: 1, insuree_LastName:"Man") {
    pageInfo {
      hasNextPage
      endCursor
    }
    edges {
      cursor
      node {
        id
        status
        insuree {
          id
          lastName
          otherNames
        }
      }
    }
  }
}
```


### Pagination

To query the first page of a resultset, we can do:
```
claims(first:10, insuree_LastName:"Man") {
    pageInfo {
      hasNextPage
      endCursor
    }
    (...)
```

`first: 10` will provide at most 10 rows, `hasNextPage` will be true if there are more records
and `endCursor` can be used to query the page:
```
claims(first:10, after: "xxxxxxxxxx=", insuree_LastName:"Man") {
    pageInfo {
      hasNextPage
      endCursor
    }
    (...)
```

### Mutations

Mutations are documented like queries and used almost in the same way. For example:
```
mutation {
  createClaimDiagnosisCode(input: {
    code: "TST"
    name: "Test2"
    validityFrom: "2019-01-01T00:00:00Z"
    validityTo: "2019-12-31T00:00:00Z"
  }
  ) {
    clientMutationId
    claimDiagnosisCode {
      id
      name
      code
    }
    errors {
      field
      messages
    }
  }
}
```

This calls the `createClaimDiagnosisCode` mutation and provides an object to save. In this case,
it has the same format as the queried object.
If the mutation encountered errors, they will be reported in the errors section of the answer. Otherwise,
the `claimDiagnosisCode` section will contain the created/updated resource.

## Server-side

### Modularity

Each module can expose a schema.py module that contains a Query object. This will automatically expose its
resources to the GraphQL endpoint.

### Exposing resources

TBC

### Mutations

To modify resources, GraphQL is using *mutations*. There are various ways to use them with Graphene:
* Plain and simple mutations (when there is one integer parameter for example)
* Form based mutations (you create a form from scratch)
* Model-Form based mutations (the form is based on a model)
* Serializer based mutations (when sharing code with REST endpoints)

#### Plain mutations

When submitting an existing claim, we only need a claim ID as parameter. This can be done this way:
```
class SubmitClaimMutation(graphene.Mutation):
    class Arguments:
        id = graphene.ID()

    claim = graphene.Field(ClaimGQLType)

    def mutate(self, info, id):
        # TODO: dummy example, no access right check, dummy model update
        claim = Claim.objects.get(pk=id)
        claim.submit_stamp = now()
        claim.save()
        return SubmitClaimMutation(claim=claim)
        
class Mutation(graphene.ObjectType):
    submit_claim = SubmitClaimMutation.Field()
    (...)
```

In this scenario, the mutation is a simple function call with a simple parameter.

#### Form based mutations

In situations where the object provided to mutate data is more complex but not directly based on a model,
one can use forms. They are usually declared in `forms.py` while mutations are in `schema.py`.

forms.py:
```
TBC
```

schema.py:
```
TBC
```

#### Model-Form based mutations

When the mutations are basically saving a database object, one can skip a lot of the boilerplate of forms.
Here is an example saving a smaller object:
forms.py:
```
class ClaimOfficerForm(forms.ModelForm):
    class Meta:
        model = ClaimOfficer
        fields = [
            "code",
            "last_name",
            "first_name",
        ]
```

schema.py:
```
class CreateClaimOfficerMutation(DjangoModelFormMutation):
    claim_officer = Field(ClaimOfficerGQLType)

    # @classmethod
    # def perform_mutate(cls, form, info):
    #     pass

    class Meta:
        form_class = ClaimOfficerForm

class Mutation(graphene.ObjectType):
    create_claim_officer = CreateClaimOfficerMutation.Field()
```

As written above, the mutation will save new objects as the id is not in the fields.
Otherwise, it would create or update the object.
You will probably want better control over this, for example to add the `audit_user_id` from the session.
This can be done from the `perform_mutate` function. If defined, it will be called in place of the default
one. So just using `pass` as in our sample would in fact not do anything.

Before this mutate is called, of course, the form is_valid will be called first.

#### REST Serializer based mutations

When a REST interface is also available and is using Serializer classes, these can be reused for Graphene:
serializers.py:
```
from rest_framework import serializers

class ClaimSerializer(serializers.Serializer):
    status = serializers.IntegerField(min_value=-4, max_value=4, required=False)
    audit_user_id = serializers.CharField(required=False)
    # ...

    def create(self, validated_data):
        audit_user_id = self.context["request"].user
        status = validated_data.get("status", None)
        if status is None:
            status = default_status()

        claim = Claim(
            status=status,
            audit_user_id=audit_user_id,
            comment=validated_data.get("comment"),
            #...
        )
        claim.save()
        return claim

    def update(self, instance, validated_data):
        instance.status = validated_data.get("status", NEW)
        # ...
        instance.save()
        return instance

```

schema.py:
```
from graphene_django.rest_framework.mutation import SerializerMutation

class CreateClaimRestMutation(SerializerMutation):
    class Meta:
        serializer_class = CreateClaimSerializer
        model_operations = ['create', 'update']
        lookup_field = 'id'
```

