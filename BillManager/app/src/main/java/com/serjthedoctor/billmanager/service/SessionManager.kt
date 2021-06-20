package com.serjthedoctor.billmanager.service

import android.content.Context
import android.content.SharedPreferences
import com.serjthedoctor.billmanager.R
import com.serjthedoctor.billmanager.domain.User

class SessionManager (context: Context) {
    private var prefs: SharedPreferences = context.getSharedPreferences(
        context.getString(R.string.app_name),
        Context.MODE_PRIVATE
    )

    companion object {
        const val AUTH_TOKEN_KEY = "auth_token"
        const val USER_ID_KEY = "user_id"
    }

    fun setAuth(user: User, token: String) {
        val editor = prefs.edit()

        editor.putString(AUTH_TOKEN_KEY, token)
        user.id?.let { editor.putInt(USER_ID_KEY, it) }

        editor.apply()
    }

    fun getAuthToken(): String? {

        return prefs.getString(AUTH_TOKEN_KEY, null)
    }

    fun clearAuthToken() {
        prefs.edit()
            .remove(AUTH_TOKEN_KEY)
            .remove(USER_ID_KEY)
            .apply()
    }

    fun getUserId(): Int {
        return prefs.getInt(USER_ID_KEY, -1)
    }
}