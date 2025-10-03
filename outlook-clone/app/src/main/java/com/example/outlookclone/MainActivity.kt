package com.example.outlookclone

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.navigation.NavHostController
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController
import com.example.shared.model.EmailFolder
import com.example.shared.model.EmailMessage
import com.example.shared.model.NewMessageRequest
import io.ktor.client.HttpClient
import io.ktor.client.call.body
import io.ktor.client.engine.okhttp.OkHttp
import io.ktor.client.plugins.contentnegotiation.ContentNegotiation
import io.ktor.client.request.*
import io.ktor.serialization.kotlinx.json.json
import kotlinx.serialization.json.Json
import kotlinx.coroutines.launch

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent { App() }
    }
}

@Composable
fun App() {
    val navController = rememberNavController()
    val httpClient = remember {
        HttpClient(OkHttp) {
            install(ContentNegotiation) {
                json(Json { ignoreUnknownKeys = true })
            }
        }
    }
    Surface(modifier = Modifier.fillMaxSize()) {
        NavHost(navController = navController, startDestination = "folders") {
            composable("folders") { FolderListScreen(httpClient, navController) }
            composable("messages/{folderId}") { backStackEntry ->
                val folderId = backStackEntry.arguments?.getString("folderId") ?: "inbox"
                MessageListScreen(httpClient, navController, folderId)
            }
            composable("message/{messageId}") { backStackEntry ->
                val messageId = backStackEntry.arguments?.getString("messageId") ?: ""
                MessageDetailScreen(httpClient, messageId)
            }
            composable("compose") { ComposeScreen(httpClient, navController) }
        }
    }
}

@Composable
fun FolderListScreen(client: HttpClient, nav: NavHostController) {
    var folders by remember { mutableStateOf<List<EmailFolder>>(emptyList()) }
    LaunchedEffect(Unit) {
        folders = client.get("http://10.0.2.2:8080/folders").body()
    }
    Scaffold(topBar = { TopAppBar(title = { Text("Folders") }) },
        floatingActionButton = {
            FloatingActionButton(onClick = { nav.navigate("compose") }) { Text("+") }
        }) { padding ->
        LazyColumn(contentPadding = padding) {
            items(folders) { folder ->
                ListItem(
                    headlineContent = { Text(folder.name) },
                    modifier = Modifier
                        .fillMaxWidth()
                        .clickable { nav.navigate("messages/${folder.id}") }
                        .padding(horizontal = 8.dp)
                )
                Divider()
            }
        }
    }
}

@Composable
fun MessageListScreen(client: HttpClient, nav: NavHostController, folderId: String) {
    var messages by remember { mutableStateOf<List<EmailMessage>>(emptyList()) }
    LaunchedEffect(folderId) {
        messages = client.get("http://10.0.2.2:8080/messages/$folderId").body()
    }
    Scaffold(topBar = { TopAppBar(title = { Text("Messages") }) }) { padding ->
        LazyColumn(contentPadding = padding) {
            items(messages) { msg ->
                ListItem(
                    headlineContent = { Text(msg.subject) },
                    supportingContent = { Text(msg.preview) },
                    modifier = Modifier
                        .fillMaxWidth()
                        .clickable { nav.navigate("message/${msg.id}") }
                        .padding(horizontal = 8.dp)
                )
                Divider()
            }
        }
    }
}

@Composable
fun MessageDetailScreen(client: HttpClient, messageId: String) {
    var message by remember { mutableStateOf<EmailMessage?>(null) }
    LaunchedEffect(messageId) {
        message = client.get("http://10.0.2.2:8080/message/$messageId").body()
    }
    Scaffold(topBar = { TopAppBar(title = { Text(message?.subject ?: "Message") }) }) { padding ->
        Column(modifier = Modifier.padding(padding).padding(16.dp)) {
            Text(text = message?.body ?: "", style = MaterialTheme.typography.bodyLarge)
        }
    }
}

@Composable
fun ComposeScreen(client: HttpClient, nav: NavHostController) {
    var to by remember { mutableStateOf("") }
    var subject by remember { mutableStateOf("") }
    var body by remember { mutableStateOf("") }
    val coroutineScope = rememberCoroutineScope()
    Scaffold(topBar = { TopAppBar(title = { Text("Compose") }) },
        floatingActionButton = {
            FloatingActionButton(onClick = {
                val req = NewMessageRequest(to = to, subject = subject, body = body)
                coroutineScope.launch {
                    client.post("http://10.0.2.2:8080/send") {
                        contentType(io.ktor.http.ContentType.Application.Json)
                        setBody(req)
                    }
                    nav.popBackStack()
                }
            }) { Text("Send") }
        }) { padding ->
        Column(modifier = Modifier.padding(padding).padding(16.dp)) {
            OutlinedTextField(value = to, onValueChange = { to = it }, label = { Text("To") }, modifier = Modifier.fillMaxWidth())
            Spacer(Modifier.height(8.dp))
            OutlinedTextField(value = subject, onValueChange = { subject = it }, label = { Text("Subject") }, modifier = Modifier.fillMaxWidth())
            Spacer(Modifier.height(8.dp))
            OutlinedTextField(value = body, onValueChange = { body = it }, label = { Text("Body") }, modifier = Modifier.fillMaxWidth(), minLines = 6)
        }
    }
}
