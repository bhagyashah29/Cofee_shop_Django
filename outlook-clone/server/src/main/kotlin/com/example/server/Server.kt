package com.example.server

import com.example.shared.model.EmailFolder
import com.example.shared.model.EmailMessage
import com.example.shared.model.NewMessageRequest
import io.ktor.serialization.kotlinx.json.*
import io.ktor.server.application.*
import io.ktor.server.engine.*
import io.ktor.server.netty.*
import io.ktor.server.plugins.contentnegotiation.*
import io.ktor.server.request.*
import io.ktor.server.response.*
import io.ktor.server.routing.*
import kotlinx.serialization.json.Json
import java.util.concurrent.ConcurrentHashMap

fun main() {
    embeddedServer(Netty, port = 8080, host = "0.0.0.0") {
        install(ContentNegotiation) {
            json(Json { prettyPrint = true; ignoreUnknownKeys = true })
        }
        routing {
            get("/") { call.respondText("Outlook Clone Server Running") }

            val folders = listOf(
                EmailFolder("inbox", "Inbox"),
                EmailFolder("sent", "Sent"),
                EmailFolder("drafts", "Drafts"),
                EmailFolder("trash", "Trash"),
            )

            val messages = ConcurrentHashMap<String, EmailMessage>()

            // Seed a few messages
            repeat(10) { i ->
                val id = "msg_$i"
                messages[id] = EmailMessage(
                    id = id,
                    folderId = if (i % 2 == 0) "inbox" else "sent",
                    subject = "Welcome $i",
                    preview = "This is a preview for message $i",
                    body = "Hello, this is the body for message $i"
                )
            }

            get("/folders") { call.respond(folders) }

            get("/messages/{folderId}") {
                val folderId = call.parameters["folderId"] ?: return@get call.respondText("Missing folderId", status = io.ktor.http.HttpStatusCode.BadRequest)
                val list = messages.values.filter { it.folderId == folderId }.sortedBy { it.id }
                call.respond(list)
            }

            get("/message/{id}") {
                val id = call.parameters["id"] ?: return@get call.respondText("Missing id", status = io.ktor.http.HttpStatusCode.BadRequest)
                val msg = messages[id] ?: return@get call.respondText("Not found", status = io.ktor.http.HttpStatusCode.NotFound)
                call.respond(msg)
            }

            post("/send") {
                val req = call.receive<NewMessageRequest>()
                val id = "msg_${System.currentTimeMillis()}"
                val msg = EmailMessage(
                    id = id,
                    folderId = "sent",
                    subject = req.subject,
                    preview = req.body.take(80),
                    body = req.body
                )
                messages[id] = msg
                call.respond(msg)
            }
        }
    }.start(wait = true)
}
