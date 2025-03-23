def create_json_history(user_question: str, ai_response: str):
    external_history = [
            {
                "role": "user",
                "type": "text",
                "content": user_question
            },
            {
                "role": "system",
                "type": "text",
                "content": ai_response
            }
        ]


    return external_history