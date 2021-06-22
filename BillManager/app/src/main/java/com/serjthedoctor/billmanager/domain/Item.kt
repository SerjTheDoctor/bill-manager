package com.serjthedoctor.billmanager.domain

import java.io.Serializable

data class Item (
    var id: Int?,
    var name: String?,
    var unit: String?,
    var unitPrice: Float?,
    var quantity: Float?,
    var price: Float?
) : Serializable
