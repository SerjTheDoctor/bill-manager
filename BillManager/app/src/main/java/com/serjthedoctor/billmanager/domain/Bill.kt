package com.serjthedoctor.billmanager.domain

import androidx.room.Entity
import androidx.room.PrimaryKey
import java.io.Serializable

@Entity(tableName = "bills")
data class Bill (
    @PrimaryKey
    var id: Int?,
    var title: String,
    var location: String,
) : Serializable
