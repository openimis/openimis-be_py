try { 
        $response = iwr http://localhost:8000/ht/?format=json -TimeoutSec 3;
        if ($response.StatusCode -eq 200) { 
            exit 0 
        } else { 
            exit 1 
            }; 
        } 
catch { 
        exit 1 
    } 