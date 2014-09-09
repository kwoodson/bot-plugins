#!/usr/bin/env ruby
#
#
require 'rubygems'
require 'sqlite3'

DBNAME="shift_builds.db"
$DB = SQLite3::Database.new(DBNAME)

result = $DB.execute("select * from builds")

result.each { |build|
    p build
    puts
}
$DB.close()
