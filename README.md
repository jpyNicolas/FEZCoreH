# FEZCore API Documentation.

This document provides example requests for each endpoint defined in the FEZCore API.

## Base URL

Assume the base URL for the API is `https://{BASE_URL}`.

### Table of Contents

1. [Signup](#signup)
2. [Login For Access Token](#login-for-access-token)
3. [Get Access Token From Refresh Token](#get-access-token-from-refresh-token)
4. [Confirm Account](#confirm-account)
5. [Resend Confirmation](#resend-confirmation)
6. [Send Recovery Password Mail](#send-recovery-password-mail)
7. [Recovery Password](#recovery-password)
8. [Get User](#get-user)
9. [Change Password](#change-password)
10. [Generate Apikey](#generate-apikey)
11. [Get Apikey Detail](#get-apikey-detail)
12. [Create Project](#create-project)
13. [Get Project](#get-project)
14. [Upload File](#upload-file)

### Run project

```bash
./start.sh
```

---

## Endpoints

### 1. Signup `/auth/signup` <a name="signup"></a>

- **Method:** POST
- **Summary:** Signup
- **Success Response:** `201 Successful Response`

**Curl Example:**

```bash
curl -X POST "https://{BASE_URL}/auth/signup" \
-H "Content-Type: application/json" \
-d '{
  "email": "user@example.com",
  "password": "your-strong-password",
  "name": "Mark"
}'
```

---

### 2. Login For Access Token `/auth/token` <a name="login-for-access-token"></a>

- **Method:** POST
- **Summary:** Login For Access Token
- **Success Response:** `200 Successful Response`

**Curl Example:**

```bash
curl -X POST "https://{BASE_URL}/auth/token" \
-H "Content-Type: application/x-www-form-urlencoded" \
-d 'username=user@example.com&password=your-strong-password'
```

---

### 3. Get Access Token From Refresh Token `/auth/refresh` <a name="get-access-token-from-refresh-token"></a>

- **Method:** GET
- **Summary:** Get Access Token From Refresh Token
- **Success Response:** `200 Successful Response`

**Curl Example:**

```bash
curl -X GET "https://{BASE_URL}/auth/refresh?refresh_token=your_refresh_token"
```

---

### 4. Confirm Account `/auth/confirm` <a name="confirm-account"></a>

- **Method:** POST
- **Summary:** Confirm Account
- **Success Response:** `204 Successful Response`

**Curl Example:**

```bash
curl -X POST "https://{BASE_URL}/auth/confirm" \
-H "Content-Type: application/json" \
-d '{
  "email": "user@example.com",
  "code": "confirmation_code"
}'
```

---

### 5. Resend Confirmation `/auth/resend-confirmation` <a name="resend-confirmation"></a>

- **Method:** POST
- **Summary:** Resend Confirmation
- **Success Response:** `204 Successful Response`

**Curl Example:**

```bash
curl -X POST "https://{BASE_URL}/auth/resend-confirmation?email=user@example.com"
```

---

### 6. Send Recovery Password Mail `/auth/send-reset-password-code` <a name="send-recovery-password-mail"></a>

- **Method:** GET
- **Summary:** Send Recovery Password Mail
- **Success Response:** `200 Successful Response`

**Curl Example:**

```bash
curl -X GET "https://{BASE_URL}/auth/send-reset-password-code?email=user@example.com"
```

---

### 7. Recovery Password `/auth/reset-password` <a name="recovery-password"></a>

- **Method:** POST
- **Summary:** Recovery Password
- **Success Response:** `204 Successful Response`

**Curl Example:**

```bash
curl -X POST "https://{BASE_URL}/auth/reset-password" \
-H "Content-Type: application/json" \
-d '{
  "email": "user@example.com",
  "code": "recovery_code",
  "password": "new_password"
}'
```

---

### 8. Get User Details `/user/` <a name="get-user"></a>

- **Method:** GET
- **Summary:** Get User
- **Success Response:** `200 Successful Response`

**Curl Example:**

```bash
curl -X GET "https://{BASE_URL}/user/" \
-H "Authorization: Bearer your_jwt_token"
```

---

### 9. Change Password `/user/change-password` <a name="change-password"></a>

- **Method:** PUT
- **Summary:** Change Password
- **Success Response:** `202 Successful Response`

**Curl Example:**

```bash
curl -X PUT "https://{BASE_URL}/user/change-password" \
-H "Content-Type: application/json" \
-H "Authorization: Bearer your_jwt_token" \
-d '{
  "current_password": "old_password",
  "new_password": "new_password"
}'
```

---

### 10. Generate Apikey `/user/generate-apikey` <a name="generate-apikey"></a>

- **Method:** POST
- **Summary:** Generate Apikey
- **Success Response:** `200 Successful Response`

**Curl Example:**

```bash
curl -X POST "https://{BASE_URL}/apikey/generate-apikey?name=apikey_name" \
-H "Authorization: Bearer your_jwt_token"
```

---

### 11. Get Apikey Detail `/apikey/` <a name="get-apikey-detail"></a>

- **Method:** GET
- **Summary:** Get Apikey Detail
- **Success Response:** `200 Successful Response`

**Curl Example:**

```bash
curl -X GET "https://{BASE_URL}/apikey/?key=your_apikey" \
-H "Authorization: Bearer your_jwt_token"
```

---

### 12. Create Project `/project/` <a name="create-project"></a>

- **Method:** POST
- **Summary:** Create Project
- **Success Response:** `200 Successful Response`

**Curl Example:**

```bash
curl -X POST "https://{BASE_URL}/project/?key=your_apikey" \
-H "Content-Type: application/json" \
-d '{
  "name": "project_name"
}'
```

---

### 13. Get Project Details `/project/{name}` <a name="get-project"></a>

- **Method:** GET
- **Summary:** Get Project
- **Success Response:** `200 Successful Response`

**Curl Example:**

```bash
curl -X GET "https://{BASE_URL}/project/project_name?key=your_apikey"
```

---

### 14. Upload File `/file/upload` <a name="upload-file"></a>

- **Method:** POST
- **Summary:** Upload File
- **Success Response:** `200 Successful Response`

**Curl Example:**

```bash
curl -X POST "https://{BASE_URL}/file/upload?project_name=project&key=your_apikey" \
-F "file=@path_to_your_file"
```
