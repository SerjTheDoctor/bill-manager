package com.serjthedoctor.billmanager.domain

import java.io.Serializable

data class LoginRequest (
    var email: String,
    var password: String
) : Serializable