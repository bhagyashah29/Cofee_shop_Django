package com.example.outlookclone.ui

import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.*
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Email
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import com.example.outlookclone.viewmodel.InboxViewModel

@Composable
fun InboxScreen(
    viewModel: InboxViewModel = androidx.lifecycle.viewmodel.compose.viewModel(),
    onOpenEmail: (String) -> Unit,
    onCompose: () -> Unit,
) {
    val state by viewModel.uiState.collectAsState()

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Inbox") },
                actions = {
                    IconButton(onClick = onCompose) {
                        Icon(Icons.Default.Email, contentDescription = "Compose")
                    }
                }
            )
        }
    ) { padding ->
        if (state.isLoading) {
            Box(Modifier.fillMaxSize().padding(padding), contentAlignment = Alignment.Center) {
                CircularProgressIndicator()
            }
        } else {
            LazyColumn(Modifier.fillMaxSize().padding(padding)) {
                items(state.messages) { msg ->
                    Column(
                        Modifier.fillMaxWidth().clickable { onOpenEmail(msg.id) }.padding(16.dp)
                    ) {
                        Text(text = msg.sender, fontWeight = FontWeight.Bold)
                        Spacer(Modifier.height(4.dp))
                        Text(text = msg.subject)
                        Spacer(Modifier.height(2.dp))
                        Text(text = msg.preview, style = MaterialTheme.typography.bodySmall)
                    }
                    Divider()
                }
            }
        }
    }
}
