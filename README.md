
# usage

``` bash
kam generate model            # generate model and migration

kam db:drop                   # drop database
kam db:create                 # create database
kam db:migrate                # run migrations
kam db:schema:dump            # generate database schema
kam db:seed                   # run database seed
```

## sample model generations

``` bash
kam generate model Assessment name:string year:integer
kam generate model Skill name:string assessment:references
kam generate model Credit name:string desc:string skill:references
kam generate model Validation desc:string text:text credit:references
```

# conf

`kam.yml` allows to specify app directory (default: `app`)

``` yaml
app_directory: app
```
