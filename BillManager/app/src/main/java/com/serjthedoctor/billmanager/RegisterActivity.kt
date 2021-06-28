package com.serjthedoctor.billmanager

import android.content.Intent
import androidx.appcompat.app.AppCompatActivity
import android.os.Bundle
import android.widget.Toast
import androidx.lifecycle.ViewModelProvider
import com.serjthedoctor.billmanager.databinding.ActivityRegisterBinding
import com.serjthedoctor.billmanager.domain.User
import com.serjthedoctor.billmanager.model.AuthModel
import java.util.*

class RegisterActivity : AppCompatActivity() {
    private lateinit var binding: ActivityRegisterBinding
    private lateinit var authModel: AuthModel

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityRegisterBinding.inflate(layoutInflater)
        setContentView(binding.root)

        authModel = ViewModelProvider(this).get(AuthModel::class.java)

        binding.registerToLogin.setOnClickListener {
            val intent = Intent(application, LoginActivity::class.java)
            startActivity(intent)
        }

        binding.registerSubmitButton.setOnClickListener {
            val name = binding.registerNameInput.text.toString()
            val email = binding.registerEmailInput.text.toString()
            val password = binding.registerPasswordInput.text.toString()

            authModel.register(name, email, password,
                onSuccess = { auth -> registerSuccess(auth.user) },
                onFailure = this::registerFailed
            )
        }
    }

    private fun registerSuccess(user: User) {
        Toast.makeText(
            this,
            "Logged in as ${user.name.capitalize(Locale.ROOT)}",
            Toast.LENGTH_SHORT
        ).show()

        val intent = Intent(application, MainActivity::class.java)
        startActivityForResult(intent, MAIN_ACTIVITY)
    }

    private fun registerFailed(error: String?) {
        Toast.makeText(
            applicationContext,
            "Error: $error",
            Toast.LENGTH_SHORT
        ).show()
    }

    companion object {
        const val MAIN_ACTIVITY = 1
    }
}