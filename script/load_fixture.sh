#!/bin/bash
set -e


# Use env var or default to 'openimis'
SOLUTION_NAME="${FIXTURE_SOLUTION:-openIMIS}"

# Configuration



echo "=== Fixture loading test for solution: $SOLUTION_NAME ==="

# Clone init files if SOLUTION provided
if [ "$SOLUTION_NAME" != "openIMIS" ]; then
  FIXTURE_PATH="./initialization"
  SOLUTION_PATH="$FIXTURE_PATH/$SOLUTION_NAME"
  FIXTURE_DIR="$SOLUTION_PATH/fixtures"
  echo "Cloning openIMIS solutions repo and extracting '$SOLUTION_NAME'..."
  mkdir -p "$FIXTURE_PATH"
  git clone --depth 1 https://github.com/openimis/solutions.git "$FIXTURE_PATH/tmp_solutions"

  if [ ! -d "$FIXTURE_PATH/tmp_solutions/$SOLUTION_NAME" ]; then
    echo "Solution '$SOLUTION_NAME' not found in solutions repo."
    exit 2
  fi

  mv "$FIXTURE_PATH/tmp_solutions/$SOLUTION_NAME" "$SOLUTION_PATH"
  rm -rf "$FIXTURE_PATH/tmp_solutions"
else
  FIXTURE_DIR="../fixtures"
fi


if [ -d "$FIXTURE_DIR" ]; then
  shopt -s nullglob # Ensure glob expands to nothing if no files match
  json_files=("$FIXTURE_DIR"/*.json)
  if [ ${#json_files[@]} -eq 0 ]; then
    echo "No .json files found in $FIXTURE_DIR"
  else
    for fixture_file in "${json_files[@]}"; do
      name=$(basename "$fixture_file")
      model=$(jq -r '.[0].model' "$fixture_file" 2>/dev/null)
       if [[ -z "$model" || "$model" == "null" ]]; then
        echo "⚠️  Skipping $name: couldn't determine model."
        continue
      fi

      echo "🔍 Checking model: $model from $name"

      count=$(python ../openIMIS/manage.py shell -c "from ${model%.*} import ${model#*.} as M; print(M.objects.count())" 2>/dev/null || echo 0)

      if [[ "$count" -eq 0 ]]; then
        echo "✅ Loading fixture: $fixture_file"
        if [ "$name" = "roles-right.json" ]; then
            python ../openIMIS/manage.py load_fixture_foreign_key "$fixture_file" --field name
          else
            python ../openIMIS/manage.py loaddata "$fixture_file"
          fi
        
      else
        echo "⏩ Skipping $model ($name): table not empty ($count records)."
      fi
      
     
    done
  fi
else
  echo "$FIXTURE_DIR does not exist"
fi
# Load roles-right fixture



echo "=== Fixture test complete for $SOLUTION_NAME ==="
exit 0