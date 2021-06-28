package com.serjthedoctor.billmanager.model

import android.app.Application
import android.content.Context
import android.content.Intent
import android.util.Log
import androidx.lifecycle.AndroidViewModel
import com.serjthedoctor.billmanager.LoginActivity
import com.serjthedoctor.billmanager.domain.LoginRequest
import com.serjthedoctor.billmanager.domain.AuthResponse
import com.serjthedoctor.billmanager.domain.RegisterRequest
import com.serjthedoctor.billmanager.domain.User
import com.serjthedoctor.billmanager.service.AuthService
import com.serjthedoctor.billmanager.service.CustomCallback
import com.serjthedoctor.billmanager.service.ServiceFactory
import com.serjthedoctor.billmanager.service.SessionManager
import retrofit2.Call
import retrofit2.Callback
import retrofit2.Response

class AuthModel(application: Application): AndroidViewModel(application) {
    private val app: Application = application
    private val sessionManager: SessionManager = SessionManager(application)
    private val service: AuthService = ServiceFactory.createService(
        AuthService::class.java,
        AuthService.RAILS_API
    )

    companion object {
        const val TAG = "AuthModel"
    }

    fun getUser(userId: Int,
                onSuccess: (success: User) -> Unit = { _ -> },
                onFailure: (error: String?) -> Unit = { _ -> }) {
        val token = sessionManager.getAuthToken()
        checkToken(token)

        service.get("Bearer $token", userId).enqueue(object : CustomCallback<User>(app) {
            override fun onSuccess(call: Call<User>, response: Response<User>) {
                if (response.isSuccessful) {
                    val body = response.body() as User

                    Log.d(TAG, "Fetched successfully: $body")
                    onSuccess(body)
                } else {
                    val errorMessage = "Could not get user: ${response.message()}"
                    Log.e(TAG, errorMessage)
                    onFailure(errorMessage)
                }
            }

            override fun onFailure(call: Call<User>, t: Throwable) {
                val errorMessage = "Could not get user. Error: ${t.message}"
                Log.e(TAG, errorMessage, t)
                onFailure(errorMessage)
            }
        })
    }

    fun login(email: String, password: String,
              onSuccess: (success: AuthResponse) -> Unit = { _ -> },
              onFailure: (error: String?) -> Unit = {_ -> }) {
        val requestData = LoginRequest(email, password)

        service.login(requestData).enqueue(object : CustomCallback<AuthResponse>(app) {
            override fun onSuccess(call: Call<AuthResponse>, response: Response<AuthResponse>) {
                if (response.isSuccessful) {
                    val body = response.body()

                    if (body?.user != null) {
                        val user = body.user as User
                        sessionManager.setAuth(user, body.token)
                        Log.d(TAG, "Login successfully")
                        onSuccess(body)
                    } else {
                        val errorMessage = "Invalid credentials"
                        Log.d(TAG, errorMessage)
                        onFailure(errorMessage)
                    }
                } else {
                    val errorMessage = "Login failed: ${response.message()}"
                    Log.e(TAG, errorMessage)
                    onFailure(errorMessage)
                }
            }

            override fun onFailure(call: Call<AuthResponse>, t: Throwable) {
                val errorMessage = "Login failed unexpectedly: ${t.message}"
                Log.e(TAG, errorMessage, t)
                onFailure(errorMessage)
            }
        })
    }

    fun register(name: String, email: String, password: String,
                 onSuccess: (success: AuthResponse) -> Unit = { _ -> },
                 onFailure: (error: String?) -> Unit = { _ -> }
    ) {
        val requestData = RegisterRequest(name, email, password)

        service.register(requestData).enqueue(object : CustomCallback<AuthResponse>(app) {
            override fun onSuccess(call: Call<AuthResponse>, response: Response<AuthResponse>) {
                if (response.isSuccessful) {
                    val body = response.body()

                    if (body?.user != null) {
                        val user = body.user as User
                        sessionManager.setAuth(user, body.token)
                        Log.d(TAG, "Registered successfully")
                        onSuccess(body)
                    } else {
                        val errorMessage = "User is null after registration"
                        Log.d(TAG, errorMessage)
                        onFailure(errorMessage)
                    }
                } else {
                    val errorMessage = "Register failed: ${response.message()}"
                    Log.e(TAG, errorMessage)
                    onFailure(errorMessage)
                }
            }

            override fun onFailure(call: Call<AuthResponse>, t: Throwable) {
                val errorMessage = "Register failed unexpectedly: ${t.message}"
                Log.e(TAG, errorMessage, t)
                onFailure(errorMessage)
            }
        })
    }

    private fun checkToken(token: String?) {
        if (!token.isNullOrEmpty()) return

        Log.e(BillsModel.TAG, "Null or empty token. Starting LOGIN Activity")

        val intent = Intent(app, LoginActivity::class.java)
        intent.flags = Intent.FLAG_ACTIVITY_NEW_TASK
        app.startActivity(intent)
    }
}