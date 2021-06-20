package com.serjthedoctor.billmanager.service;

import com.serjthedoctor.billmanager.domain.LoginRequest
import com.serjthedoctor.billmanager.domain.AuthResponse
import com.serjthedoctor.billmanager.domain.RegisterRequest
import com.serjthedoctor.billmanager.domain.User
import retrofit2.Call
import retrofit2.http.*

interface AuthService {
    companion object {
        const val FLASK_API = "http://192.168.0.127:5000"
        const val RAILS_API = "http://192.168.0.127:3000"
    }

    @POST("/auth/login")
    fun login(@Body request: LoginRequest): Call<AuthResponse>

    @POST("/auth/register")
    fun register(@Body request: RegisterRequest): Call<AuthResponse>

    @GET("/users/{id}")
    fun get(
        @Header("Authorization") token: String,
        @Path("id") id: Int
    ): Call<User>
}
