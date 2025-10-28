# Outlook Clone (Minimal)

This is a minimal learning project that demonstrates a basic mail flow using:
- Android App in Kotlin + Jetpack Compose
- Ktor Server (JVM) with in-memory data
- Shared Kotlin module for models (kotlinx.serialization)

Not affiliated with Microsoft. This is not a full-feature clone.

## Modules
- `app` — Android app
- `server` — Ktor server
- `shared` — Shared models

## Running
1. Start the server:
```bash
./gradlew :server:run
```
2. Run the Android app in Android Studio. The app calls `http://10.0.2.2:8080` (Android emulator host).

## Features
- List folders
- List messages by folder
- View message detail
- Compose and send (adds to Sent)
