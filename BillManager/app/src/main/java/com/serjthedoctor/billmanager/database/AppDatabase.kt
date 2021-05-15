package com.serjthedoctor.billmanager.database

import android.app.Application
import androidx.room.Room

class AppDatabase : Application() {
    lateinit var db: BillsDatabase

    override fun onCreate() {
        super.onCreate()
        db = Room
            .databaseBuilder(applicationContext, BillsDatabase::class.java, "bills_database")
            .fallbackToDestructiveMigration()
            .build()
    }
}