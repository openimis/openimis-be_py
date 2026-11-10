# ClaimGuard — Backend Assembly Notes

This fork registers the **ClaimGuard** fraud detection module in `openimis.json` for the Technikali openIMIS Hackathon submission.

**Tag:** `v1.0-hackathon`  
**PR:** [openimis/openimis-be_py#385](https://github.com/openimis/openimis-be_py/pull/385)

## Change in this fork

```json
{
  "name": "claimguard",
  "pip": "-e /openimis-be/openimis-be-claimguard_py"
}
```

The `-e` path is for Docker volume-mount development. See the full module at:

**https://github.com/Nosh-thee-techy/openimis-be-claimguard_py**

## Full stack setup

See **https://github.com/Nosh-thee-techy/openimis-dist_dkr** for Docker Compose instructions.
