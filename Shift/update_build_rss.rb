#!/usr/bin/ruby 
#
#
require 'rubygems'
require 'simple-rss'
require 'net/https'
require 'rubyful_soup'
require 'json'
require 'sqlite3'
require 'logger'

$log = Logger.new(File.join(Dir.getwd, "shift_builds.log"))
$log.info("#{$0} started at #{Time.now}") 
#require 'ruby-debug'
#Debugger.start


$TABLE_NAME="builds"

$RSS_URL = "https://ci.dev.openshift.redhat.com/jenkins/job/libra_check/api/json"
#puts File.join(Dir.getwd, "shift_builds.db")
$DB = SQLite3::Database.new("/home/kwoodson/python/Supybot-0.83.4.1/plugins/Shift/shift_builds.db")
if $DB.execute("SELECT count(*) FROM sqlite_master WHERE type='table' AND name='#{$TABLE_NAME}';")[0][0] == 0
    #DB NOT CREATED, WHAT TO DO?
    #build table and continue 
    begin
       $DB.execute("create table #{$TABLE_NAME} (" +
               "id int primary key ," +
               "name varchar(30), " +
               "status varchar(30), " +
               "date varchar(30), " +
               "duration int, " +
               "link text, " +
               "commits text)")
    rescue
        $log.error("ERROR: Couldn't create table in database")
        puts "ERROR: Couldn't create table in database"
        exit 1
    end
#else
#puts "table exists"
end

#$RSS_URI = URI.parse $RSS_URL

class Net::HTTP
  alias_method :old_initialize, :initialize
  def initialize(*args)
    old_initialize(*args)
    @ssl_context = OpenSSL::SSL::SSLContext.new
    @ssl_context.verify_mode = OpenSSL::SSL::VERIFY_NONE
  end
end

#def insert_build_values(num,name,status,date,commits)
def insert_build_values(data)
    #builds are read with latest first.  
    #reverse the order so that mysql will have latest on the bottom
    data.reverse! 
    rcode = nil
    data.each { |build|
#INSERT OR REPLACE INTO Employee (id,role,name) VALUES (  1, 'code monkey',
#(select name from Employee where id = 1));

        qstr= "'%s', " * build.size
        loc = qstr.rindex(",")
        qstr = "(" + qstr[0..loc-1] + qstr[loc+1..qstr.length] + ")"
        ins_str = "insert or replace into #{$TABLE_NAME} values " + qstr % build
            
#"('%s', '%s', '%s', '%s', '%s', '%s')" % build
#[num, name, status, date, commits]
        
        begin
            rcode = $DB.execute(ins_str)
        rescue SyntaxError => se
            puts se.message
        rescue => e
            puts "EXCEPTION: #{e.message}"
            $log.error("EXCEPTION: #{e.message}")
#puts "class: #{e.class}"
#puts "\t#{build[0]}"
#puts "\t#{build[1]}"
#puts "\t#{build[2]}"
#puts "\t#{build[3]}" 
#puts "\t#{build[4]}"
#puts "\t#{build[5]}"
        end
    }
#$DB.commit()
#return rcode
end

def get_build build_num
#debugger
    url = "https://ci.dev.openshift.redhat.com/jenkins/job/libra_check/%s/api/json"%build_num
    burl = "https://ci.dev.openshift.redhat.com/jenkins/job/libra_check/%s/"%build_num
    resp = get_url url
    resp_json = JSON.parse(resp.body)
    resp_json['artifacts'] = nil
    commits = []
    resp_json['changeSet']['items'].each { |change|
        author = change['author']['fullName'].strip()
        comment = change['comment'].strip().gsub!(/'/,"")
        id = change['id']
        commits <<  "%s | %s | %s" % [author, id, comment]
    }
    build_name = resp_json['fullDisplayName']
    build_result = resp_json['result']
    build_result ||= "building" 
    build_date = resp_json['id']
    build_duration = resp_json['duration'].to_i / 1000 / 60
    build_url = burl
    build_commits = commits.join("$$")

#puts "name=>#{build_name}"
#puts "result=>#{build_result}"
#puts "date=>#{build_date}"
#puts "commits=>#{build_commits}"
#
#puts "name=>#{build_name.class}"
#puts "result=>#{build_result.class}"
#puts "date=>#{build_date.class}"
#puts "commits=>#{build_commits.class}"

    return [build_num, build_name, build_result, build_date, build_duration, build_url, build_commits ]
end

def get_changes(html)
    rdata = []
#debugger
#puts html
    #UGLY BECAUSE SOUP WON'T TAKE SINGLE QUOTES !!!
    html.gsub!(/#039;/, "'") 
    soup = BeautifulSoup.new html 
    changes = soup.find('div', :attrs => {'class' => 'changeset-message'})
    #contents[0] commit msg
    changes.each { |commit| 
        author = commit[0].contents[1].contents.to_s
        commit_id = changes.contents[0].to_s.scan(/[a-z0-9]{32}/)

        rdata << author unless author.nil?
        rdata << commit_id unless commit_id.nil?
        rdata << changes.contents[1].contents.select { |obj| obj if obj.class == NavigableString }.join(" ")
    }
    return rdata
end


def get_url url
    res = nil
    puts "Fetching url: #{url}"
    $log.info("Fetching url: #{url}")
    url = URI.parse(url)
    begin
        req = Net::HTTP::Get.new url.path
        http = Net::HTTP.new(url.host, url.port)
        http.use_ssl = (url.scheme == "https")
        http.verify_mode = OpenSSL::SSL::VERIFY_NONE
        res = http.start { |http|
            http.request(req)
        }
    rescue => detail
        puts detail.message
        res = nil
    end
    return res
end

def do_db
end

def main
    res = get_url $RSS_URL
    data = []
    unless res.nil?
#debugger
        builds = JSON.parse(res.body)
        builds['builds'].each { |build|
            url = build['url']
            build_num = build['number']
            data << get_build(build_num)
        }
    else
        $log.error("ERROR: Could not retrieve builds.")
        puts "ERROR: Could not retrieve builds."
    end
    
    insert_build_values(data) if data.length > 0
    
end

if __FILE__ == $0
    main
end

__END__



