# LLM Chat API

## 1. Overview

The LLM Chat API allows clients to send messages to a Large Language Model and receive generated responses.

The API currently supports Ollama through LiteLLM. OpenAI is available as a planned provider option but requires configuration before use.

## 2. Endpoint

| Property | Value |
|---|---|
| Method | POST |
| Endpoint | `/api/v1/llm/chat` |
| Content-Type | `application/json` |
| Authentication | Not implemented yet |

## 3. Request Body

### Example: Ollama Provider

```json
{
  "message": "Explain Java Streams",
  "provider": "ollama"
}
```

### Example: Default Provider

The provider field is optional. If omitted, Ollama is selected by default.

```json
{
  "message": "Explain Java Streams"
}
```

## 4. Request Fields

| Field | Type | Required | Description |
|---|---|---|---|
| message | string | Yes | User's prompt or message |
| provider | string | No | LLM provider: ollama or openai |

Validation rules:

- Message must contain at least one character.
- Message maximum length is 10,000 characters.
- Provider must be either `ollama` or `openai`.
- Default provider is `ollama`.

## 5. Successful Response

HTTP Status: `200 OK`

```json
{
  "provider": "ollama",
  "response": "Java Streams allow collection processing using a functional programming style."
}
```

## 6. Error Responses

### 422 – Validation Error

Returned when the request contains invalid data.

Example: Unsupported provider.

```json
{
  "detail": [
    {
      "type": "literal_error",
      "loc": ["body", "provider"],
      "msg": "Input should be 'ollama' or 'openai'"
    }
  ]
}
```

Example: Empty message.

```json
{
  "detail": [
    {
      "type": "string_too_short",
      "loc": ["body", "message"],
      "msg": "String should have at least 1 character"
    }
  ]
}
```

### 400 – Bad Request

Returned for an unsupported provider if the service is called directly with an invalid provider value.

### 502 – Bad Gateway

Returned when the selected LLM provider request fails.

## 7. Testing

The endpoint can be tested through Swagger UI.

Swagger URL:

`http://localhost:8000/docs`

Test cases:

| Test | Input | Expected Status |
|---|---|---|
| Valid Ollama request | Valid message and ollama provider | 200 |
| Unsupported provider | Provider: gemini | 422 |
| Empty message | Empty message string | 422 |
| Default provider | Message without provider field | 200 |

## 8. Implementation Status

- LLM Chat API: Completed.
- Ollama provider: Working.
- Default provider selection: Working.
- Pydantic validation: Working.
- OpenAI provider: Pending configuration.
