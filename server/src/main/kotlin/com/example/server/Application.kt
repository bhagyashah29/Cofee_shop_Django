package com.example.server

import io.ktor.server.application.*
import io.ktor.server.engine.embeddedServer
import io.ktor.server.netty.Netty
import io.ktor.server.routing.*
import io.ktor.server.response.respond
import io.ktor.server.request.receive
import io.ktor.server.response.respondText
import io.ktor.server.plugins.contentnegotiation.*
import io.ktor.serialization.kotlinx.json.*
import io.ktor.server.plugins.cors.routing.*
import io.ktor.server.plugins.callloging.*
import kotlinx.serialization.Serializable
import java.util.concurrent.ConcurrentHashMap

fun main() {
    embeddedServer(Netty, port = 8080, host = "0.0.0.0") {
        install(ContentNegotiation) { json() }
        install(CORS) { anyHost() }
        install(CallLogging)
        routing { mailRoutes() }
    }.start(wait = true)
}

@Serializable
data class Message(
    val id: String,
    val sender: String,
    val subject: String,
    val preview: String,
    val body: String,
    val timestampEpochMs: Long
)

@Serializable
data class SendMessageRequest(val to: String, val subject: String, val body: String)
@Serializable
data class SendMessageResponse(val id: String)

private val messages = ConcurrentHashMap<String, Message>().apply {
    repeat(10) { idx ->
        val id = (idx + 1).toString()
        put(id, Message(
            id = id,
            sender = "person$idx@example.com",
            subject = "Welcome $idx",
            preview = "This is a preview for message $idx",
            body = "This is the full body of message $idx.\n\nThanks!",
            timestampEpochMs = System.currentTimeMillis() - idx * 60_000L
        ))
    }
}

fun Route.mailRoutes() {
    route("/messages") {
        get {
            call.respond(messages.values.sortedByDescending { it.timestampEpochMs })
        }
        get("/{id}") {
            val id = call.parameters["id"]
            val msg = messages[id]
            if (msg != null) call.respond(msg) else call.respondText("Not found", status = io.ktor.http.HttpStatusCode.NotFound)
        }
        post {
            val req = call.receive<SendMessageRequest>()
            val newId = (messages.size + 1).toString()
            val msg = Message(
                id = newId,
                sender = "me@example.com",
                subject = req.subject,
                preview = req.body.take(64),
                body = req.body,
                timestampEpochMs = System.currentTimeMillis()
            )
            messages[newId] = msg
            call.respond(SendMessageResponse(newId))
        }
    }
}
