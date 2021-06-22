package com.serjthedoctor.billmanager.domain

import androidx.room.Entity
import androidx.room.PrimaryKey
import java.io.Serializable
import java.time.LocalDate

// @Entity(tableName = "bills")
data class Bill (
    // @PrimaryKey
    var id: Int?,
    var name: String?,
    var status: BillStatus?,
    var date: LocalDate?,
    var merchant: String?,
    var price: Float?,
    var imageUrl: String?,

    var items: List<Item>?
) : Serializable

enum class BillStatus {
    QUEUED,
    RUNNING,
    PROCESSED
}