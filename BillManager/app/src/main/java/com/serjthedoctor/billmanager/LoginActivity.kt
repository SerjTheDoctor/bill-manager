package com.serjthedoctor.billmanager

import android.content.Intent
import androidx.appcompat.app.AppCompatActivity
import android.os.Bundle
import android.widget.Toast
import androidx.lifecycle.ViewModelProvider
import com.serjthedoctor.billmanager.databinding.ActivityLoginBinding
import com.serjthedoctor.billmanager.domain.AuthResponse
import com.serjthedoctor.billmanager.domain.User
import com.serjthedoctor.billmanager.model.AuthModel
import com.serjthedoctor.billmanager.service.SessionManager
import java.util.*

class LoginActivity : AppCompatActivity() {
    private lateinit var binding: ActivityLoginBinding
    private lateinit var authModel: AuthModel

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityLoginBinding.inflate(layoutInflater)
        setContentView(binding.root)

        authModel = ViewModelProvider(this).get(AuthModel::class.java)

        binding.loginToRegister.setOnClickListener {
            val intent = Intent(application, RegisterActivity::class.java)
            startActivity(intent)
        }

        binding.loginSubmitButton.setOnClickListener {
            val email = binding.loginEmailInput.text.toString()
            val password = binding.loginPasswordInput.text.toString()

            authModel.login(email, password,
                onSuccess = { success -> loginSuccess(success.user) },
                onFailure = this::loginFail
            )
        }
    }

    private fun loginSuccess(user: User) {
        Toast.makeText(this, "Logged in as ${user.name.capitalize(Locale.ROOT)}", Toast.LENGTH_SHORT).show()
        val intent = Intent(application, MainActivity::class.java)
        startActivityForResult(intent, MAIN_ACTIVITY)
    }

    private fun loginFail(error: String?) {
        Toast.makeText(
            applicationContext,
            "Error: $error",
            Toast.LENGTH_LONG
        ).show()
    }

    companion object {
        const val MAIN_ACTIVITY = 1
    }
}