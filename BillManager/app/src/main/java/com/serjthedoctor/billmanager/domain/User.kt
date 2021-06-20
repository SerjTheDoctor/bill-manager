package com.serjthedoctor.billmanager.domain

import androidx.room.Entity
import androidx.room.PrimaryKey
import java.io.Serializable

// @Entity(tableName = "users")
data class User (
    // @PrimaryKey
    var id: Int?,
    var name: String,
    var email: String
) : Serializable