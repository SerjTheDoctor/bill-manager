package com.serjthedoctor.billmanager.database

import androidx.lifecycle.LiveData
import androidx.room.*
import com.serjthedoctor.billmanager.domain.Bill

@Dao
interface BillsDao {

    @get:Query("select * from bills")
    val bills: LiveData<MutableList<Bill>>

//    @get:Query("select count(*) from expenses")
//    val nrExpenses: Int

//    @Query("select * from expenses where student = :student")
//    fun getExpensesByStudent(student: String): LiveData<MutableList<Expense>>

    @Insert
    fun addOne(b: Bill)

    @Insert
    fun addAll(bs: List<Bill>)

    @Update
    fun updateOne(b: Bill)

    @Delete
    fun deleteOne(b: Bill)

    @Query("delete from bills")
    fun deleteAll()
}