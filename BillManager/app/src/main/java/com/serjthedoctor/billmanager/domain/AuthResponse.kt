package com.serjthedoctor.billmanager.domain

import java.io.Serializable

data class AuthResponse (
    var token: String,
    var user: User
) : Serializable
