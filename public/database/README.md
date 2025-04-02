# 🗄️ BioLens Database Setup (Supabase)

This guide walks you through setting up the **BioLens** database on **Supabase** for seamless data storage, authentication, and chat session tracking. 📊🚀

---

## 🌟 Features
✅ User authentication & session management 🔐  
✅ Chat history storage 📝  
✅ Indexed queries for optimized performance ⚡  
✅ Secure, cloud-based database powered by **Supabase** ☁️  

---

## 🛠️ Prerequisites
- A **Supabase** account → [Sign up here](https://supabase.com/) 🔗
- Supabase **Project URL** & **API Key**
- PostgreSQL-compatible database (provided by Supabase)
- Python 3.12.8 (for integration with the BioLens app)

---

## 🚀 Step-by-Step Setup

### 1️⃣ Create a Supabase Project
1. Go to [Supabase Dashboard](https://app.supabase.com/).
2. Click **New Project** and fill in the required details.
3. Choose a **strong database password** (store it securely 🔑).
4. Click **Create Project** and wait for the database to initialize.

### 2️⃣ Configure Authentication (Optional)
By default, Supabase enables **email verification** for sign-ups. To disable it:
1. Navigate to **Authentication > Providers**.
2. Under **Email**, toggle off **Confirm email**.
3. Click **Save**.

### 3️⃣ Retrieve Database Credentials
1. Go to **Project Settings > Database**.
2. Copy the **Database URL** and **anon/public API key**.
3. Store these credentials securely as they will be used in the BioLens app.

### 4️⃣ Set Up Database Schema

Go to **SQL Editor** in Supabase and run the following SQL script to create the required tables:

```sql
-- Create users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email TEXT NOT NULL UNIQUE,
    name TEXT,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- Create chat_sessions table
CREATE TABLE chat_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    title TEXT,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Create chat_messages table
CREATE TABLE chat_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL,
    content TEXT,
    role TEXT,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES chat_sessions(id) ON DELETE CASCADE
);

-- Indexes for performance optimization
CREATE INDEX idx_chat_sessions_user_id ON chat_sessions(user_id);
CREATE INDEX idx_chat_messages_session_id ON chat_messages(session_id);
```

### 5️⃣ Connect Database to BioLens App

Add your Supabase credentials to the **`.streamlit/secrets.toml`** file:

```toml
SUPABASE_URL = "your-supabase-url"
SUPABASE_KEY = "your-supabase-key"
```

---

## 🎯 Usage
- User authentication & session tracking are managed via Supabase Auth.
- Chat sessions and messages are stored in **chat_sessions** and **chat_messages** tables.
- Data is indexed for efficient querying.

---

## 🤝 Support
If you found this setup guide helpful, ⭐ **star the repository** and share it with others! 🚀

Happy coding! 💙