# EMIS School Management System

## Deployment Instructions

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Local run

```bash
streamlit run app.py
```

### 3. Set environment variables

Create a `.env` file with:

```env
SUPABASE_URL=https://your-supabase-url.supabase.co
SUPABASE_KEY=your-supabase-service-key
```

### 4. Streamlit deploy

- Push the repo to GitHub.
- Open Streamlit Community Cloud.
- Connect the GitHub repo.
- Set `app.py` as the main file.
- Add the same secrets under App Settings > Secrets.

### 5. Notes

- Do not commit `.env`.
- `emis.db` is local storage and not persistent on cloud.
- For production, use hosted Supabase or another managed database.
