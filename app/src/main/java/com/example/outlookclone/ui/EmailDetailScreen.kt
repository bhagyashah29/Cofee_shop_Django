package com.example.outlookclone.ui

import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import com.example.outlookclone.viewmodel.EmailDetailViewModel

@Composable
fun EmailDetailScreen(
    id: String,
    viewModel: EmailDetailViewModel = androidx.lifecycle.viewmodel.compose.viewModel(),
    onBack: () -> Unit
) {
    val message by viewModel.state.collectAsState()
    LaunchedEffect(id) { viewModel.load(id) }
    Scaffold(topBar = { TopAppBar(title = { Text(message?.subject ?: "Email") }) }) { padding ->
        Column(Modifier.fillMaxSize().padding(padding).padding(16.dp)) {
            if (message == null) {
                CircularProgressIndicator()
            } else {
                Text(text = "From: ${message!!.sender}")
                Spacer(Modifier.height(8.dp))
                Text(text = message!!.body)
                Spacer(Modifier.height(16.dp))
                Button(onClick = onBack) { Text("Back") }
            }
        }
    }
}
