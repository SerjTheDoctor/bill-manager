package com.serjthedoctor.billmanager.domain

import java.io.Serializable

data class RegisterRequest (
    var name: String,
    var email: String,
    var password: String
) : Serializable
