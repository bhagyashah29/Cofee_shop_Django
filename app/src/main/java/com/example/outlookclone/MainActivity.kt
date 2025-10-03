package com.example.outlookclone

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.navigation.NavHostController
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController
import com.example.outlookclone.ui.ComposeMailScreen
import com.example.outlookclone.ui.EmailDetailScreen
import com.example.outlookclone.ui.InboxScreen
import com.example.outlookclone.ui.theme.AppTheme

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            AppTheme {
                Surface(color = MaterialTheme.colorScheme.background) {
                    OutlookNavHost()
                }
            }
        }
    }
}

sealed class Routes(val route: String) {
    data object Inbox : Routes("inbox")
    data object Detail : Routes("detail/{id}")
    data object Compose : Routes("compose")
}

@Composable
fun OutlookNavHost(navController: NavHostController = rememberNavController()) {
    NavHost(navController = navController, startDestination = Routes.Inbox.route) {
        composable(Routes.Inbox.route) {
            InboxScreen(onOpenEmail = { id ->
                navController.navigate("detail/$id")
            }, onCompose = {
                navController.navigate(Routes.Compose.route)
            })
        }
        composable(Routes.Detail.route) { backStackEntry ->
            val id = backStackEntry.arguments?.getString("id") ?: ""
            EmailDetailScreen(id = id, onBack = { navController.popBackStack() })
        }
        composable(Routes.Compose.route) {
            ComposeMailScreen(onBack = { navController.popBackStack() })
        }
    }
}
