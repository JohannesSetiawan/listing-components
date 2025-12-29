On "Audit Trail" page, create new section ABOVE the response body JSON form that display the fetched data in a more readable version. The audit trail APi will always returns list of data in forms of JSON object (so the response body is in form of {"data":[{obj1}, {obj2}]}). 

An example of 1 item in the list is in file example.json. I want you for each list items to show the details of the information as below:
1. the action that was made (from "action")
2. The Automation ID (from "new_data".automation_id if existed, else empty string "")
3. The updated data (from "new_data"). Make a pop up to show the full JSON in pretty mode. DO not show the full data in the list, truncate it to max 200 character
4. The old data (from "old_data"). Make a pop up to show the full JSON in pretty mode. DO not show the full data in the list, truncate it to max 200 character
