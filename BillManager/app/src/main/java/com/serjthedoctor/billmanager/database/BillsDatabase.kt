package com.serjthedoctor.billmanager.database

import androidx.room.Database
import androidx.room.RoomDatabase
import com.serjthedoctor.billmanager.domain.Bill

// @Database(entities = [Bill::class], version = 1, exportSchema = false)
abstract class BillsDatabase : RoomDatabase() {
    abstract val billsDao: BillsDao
}