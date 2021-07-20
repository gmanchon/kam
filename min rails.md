
# app

``` bash
.
├── app
│   ├── controllers
│   │   └── application_controller.rb
│   ├── models
│   └── views
│       └── layouts
│           └── application.html.erb
└── config
    ├── database.yml
    └── routes.rb
```

# migration

``` bash
rails generate model Restaurant name:string rating:integer
```

``` bash
kam generate model Assessment name:string enterprise:string

kam generate model Skill name:string assessment:references
kam generate model Credit name:string desc:string skill:references
kam generate model Validation desc:string credit:references

kam generate model Session name:string assessment:references
kam generate model Candidate github_nickname:string batch:string exam_repo:string exam_repo_2:string api_repo:string api_prod_url:string session:references
```

``` bash
# invoke  active_record
```

``` ruby
# db/migrate/YYYYMMDDHHMMSS_create_restaurants.rb
class CreateRestaurants < ActiveRecord::Migration[6.0]
  def change
    create_table :restaurants do |t|
      t.string :name
      t.integer :rating

      t.timestamps
    end
  end
end
```

``` ruby
# app/models/restaurant.rb
class Restaurant < ApplicationRecord
end
```

``` bash
rails db:migrate  # => generates db/schema.rb
```

``` bash
rails g migration AddAddressToRestaurants
```

``` ruby
# db/migrate/YYYYMMDDHHMMSS_add_address_to_restaurants.rb

class AddAddressToRestaurants < ActiveRecord::Migration[6.0]
  def change
    add_column :restaurants, :address, :string
    # add_column
    # change_column
    # rename_column
    # remove_column
    # add_reference
  end
end
```

``` bash
rails db:migrate
```

``` bash
rails db:drop
rails db:create
rails db:migrate  # run pending migrations
rails db:rollback
rails db:reset  # drop + create tables in schema.rb
```

``` ruby
@restaurants = Restaurants.all  # index

@restaurant = Restaurants.find(params[:id])  # show

@restaurant = Restaurants.new  # new

@restaurant = Restaurants.new(params[:restaurant])  # create
@restaurant.save

@restaurant = Restaurants.find(params[:id])  # edit
@restaurant.update(params.require(:restaurant).permit(:name, :rating, :address))  # update
@restaurant.save

@restaurant = Restaurants.find(params[:id])  # delete
@restaurant.destroy
```

# seed

``` bash
rails db:seed  # db/seeds.rb
```

``` ruby
# db/seeds.rb
puts "Cleaning database..."
Restaurant.destroy_all

puts "Creating restaurants..."
dishoom = { name: "Dishoom", address: "7 Boundary St, London E2 7JE", stars: 5 }
pizza_east =  { name: "Pizza East", address: "56A Shoreditch High St, London E1 6PQ", stars: 4 }

[ dishoom, pizza_east ].each do |attributes|
  restaurant = Restaurant.create!(attributes)
  puts "Created #{restaurant.name}"
end
puts "Finished!"
```

# active record

``` ruby
@restaurants = Restaurant.where(stars: 5)
```

``` bash
rails generate migration AddChefNameToRestaurants chef_name:string
rails db:migrate
```

# models

``` ruby
# app/models/restaurant.rb
class Restaurant < ApplicationRecord
  has_many :reviews, dependent: :destroy
end

# app/models/review.rb
class Review < ApplicationRecord
  belongs_to :restaurant
end
```

``` bash
rails g controller reviews
```

``` ruby
  def create
    @review = Review.new(review_params)
    @restaurant = Restaurant.find(params[:restaurant_id])
    @review.restaurant = @restaurant
    @review.save
  end
```
