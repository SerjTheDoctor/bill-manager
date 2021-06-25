package com.serjthedoctor.billmanager.lib

fun String.limit(chars: Int): String {
    return if (length < chars) {
        this
    } else {
        this.substring(0, chars - 3) + "..."
    }
}