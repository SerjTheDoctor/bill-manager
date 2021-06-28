package com.serjthedoctor.billmanager.domain

import java.io.Serializable
import java.time.LocalDate

data class Product(
    var id: Int?,
    var name: String?,
    var unit: String?,
    var unitPrice: Float?,
    var merchant: String?,
    var date: LocalDate?
) : Serializable
