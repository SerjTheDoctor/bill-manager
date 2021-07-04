# This file should contain all the record creation needed to seed the database with its default values.
# The data can then be loaded with the bin/rails db:seed command (or created alongside the database with db:setup).
#
# Examples:
#
#   movies = Movie.create([{ name: 'Star Wars' }, { name: 'Lord of the Rings' }])
#   Character.create(name: 'Luke', movie: movies.first)
require 'faker'

merchants = ['Profi', 'Auchan', 'Safeway Store', 'Lidl']
units = %w[buc kg por]

user = User.create(name: 'John', email: 'john@gmail.com', password: 'pass')

10.times do
    bill = user.create_bill(
        merchants.sample,
        # Faker::LoremPixel.image,
        [
            Faker::Number.decimal(l_digits: 2, r_digits: 2),    #  12.34
            Faker::Number.decimal(l_digits: 3, r_digits: 2)     # 123.45
        ].sample,
        Faker::Date.between(from: '2020-01-01', to: '2021-05-05'),
    )

    rand(1..5).times do
        unit_price = [
            Faker::Number.decimal(l_digits: 1, r_digits: 2),    #  1.23
            Faker::Number.decimal(l_digits: 2, r_digits: 2)     # 12.34
        ].sample
        unit = units.sample
        quantity = unit == 'kg' ? Faker::Number.decimal(l_digits: 1, r_digits: 3) : rand(10)

        bill.items.create!(
            name: [Faker::Food.dish, Faker::Food.fruits, Faker::Food.vegetables].sample,
            unit: unit,
            unit_price: unit_price,
            quantity: quantity,
            price: unit_price * quantity
        )
    end
end