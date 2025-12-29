Create new feature called "Audit Trail" that works like below:

1. User input the audit trail URL, for example: https://<api>/v1/nocode/record/audit_trail (the format is not strict, no need to validate)
2. User input the authorizzation token for authorization header using JWT bearer token. 
3. User input the form_data_id and record_id.
4. System makes POST request to that URL using auth header and the request body is like below:
{
    "form_data_id": "sdsdcsdsdc",
    "page": 1,
    "limit": 500,
    "sort": {
        "timestamp": -1
    },
    "filter": {
        "record_id": "sdcddsd"
    }
}
5. Returns the JSON response to the user in pretty form.