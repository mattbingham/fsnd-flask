#!/usr/bin/env python3.5

from http.server import HTTPServer, BaseHTTPRequestHandler
import cgi
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from database_setup import Base, Restaurant, MenuItem

# Database stuff
engine = create_engine('sqlite:///restaurantMenu.db')
Base.metadata.bind=engine
DBSession = sessionmaker(bind = engine)
session = DBSession()

class WebServerHandler(BaseHTTPRequestHandler):

    # Let's add boring repetative stuff here
    form_html = \
'''
<form method='POST' enctype='multipart/form-data' action='/hello'>
    <h2>What would you like me to say?</h2>
    <input name="message" type="text">
    <input type="submit" value="Submit" >
</form>
 '''
    form_restaurant = \
'''
<form method='POST' enctype='multipart/form-data' action='/restaurants/new'>
    <h2>Make a new restaurant</h2>
    <input name="newRestaurantName" type="text">
    <input type="submit" value="Create" >
</form>
 '''
    open_tags = "<html>\n<body>"
    close_tags = "\n</body>\n</html>"

    def do_GET(self):
        try:
            # restaurants list

            if self.path.endswith("/restaurants"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()

                output = self.open_tags + "<h1>Restaurants</h1>"
                output += '<a href="restaurants/new">New restaurant</a>'

                # Database query
                restaurants = session.query(Restaurant).all()
                for restaurant in restaurants:
                    output +="<h2>{}</h2>".format(restaurant.name)
                    output += '<a href="{}/edit">Edit</a><br>'.format(restaurant.id)
                    output += '<a href="delete">Delete</a>'.format(restaurant.id)

                output += self.close_tags
                self.wfile.write(output.encode())
                print(output)
            
            # Create new restaurant
            if self.path.endswith("/restaurants/new"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                output = self.open_tags
                output += "<h1>Make a new restaurant!</h1>" + self.form_restaurant
                output += self.close_tags
                self.wfile.write(output.encode())
                return

            # Edit restaurant
            if self.path.endswith("/edit"):
                restaurantIDPath = self.path.split("/")[2]
                myRestaurantQuery = session.query(Restaurant).filter_by(id=restaurantIDPath).one()

                if myRestaurantQuery is not []:
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    output = self.open_tags
                    output += "<h1>{}</h1>".format(myRestaurantQuery)
                    output += "<form method='POST' enctype='multipart/form-data' action = '/restaurants/%s/edit' >" % restaurantIDPath
                    output += "<input name = 'newRestaurantName' type='text' placeholder = '%s' >" % myRestaurantQuery.name
                    output += "<input type = 'submit' value = 'Rename'>"
                    output += "</form>"
                    output += self.close_tags
                    self.wfile.write(output.encode())

            # hello URL
            if self.path.endswith("/hello"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                output = self.open_tags
                output += "<h1>Hello!</h1>" + self.form_html
                output += self.close_tags
                self.wfile.write(output.encode())
                print(output)

            # hola URL
            if self.path.endswith("/hola"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()

                output = self.open_tags
                output += "<h1>&#161;Hola!</h1>" + self.form_html
                output += "<a href='/hello'>Back to Hello</a>"
                output += self.close_tags
                self.wfile.write(output.encode())
                print(output)



        except IOError:
            self.send_error(404, "File Not Found {}".format(self.path))

    def do_POST(self):
        try:
            if self.path.endswith("/edit"):
                ctype, pdict = cgi.parse_header(
                self.headers['content-type'])
                pdict['boundary'] = bytes(pdict['boundary'], "utf-8")

                if ctype == 'multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile, pdict)
                    messagecontent = fields.get('newRestaurantName')
                    restaurantIDPath = self.path.split("/")[2]

            if self.path.endswith("/restaurants/new"):
                ctype, pdict = cgi.parse_header(
                self.headers['content-type'])

                pdict['boundary'] = bytes(pdict['boundary'], "utf-8")

                if ctype == 'multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile, pdict)
                    messagecontent = fields.get('newRestaurantName')
            
            # Create new restaurant object
            newRestaurant = Restaurant(name=messagecontent[0])
            session.add(newRestaurant)
            session.commit()

            self.send_response(301)
            self.send_header('Content-type', 'text/html')
            self.send_header('Location', '/restaurants')
            self.end_headers()

            # self.send_response(301)
            # self.send_header('Content-type', 'text/html')
            # self.end_headers()

            # ctype, pdict = cgi.parse_header(
            #     self.headers['content-type'])

            # pdict['boundary'] = bytes(pdict['boundary'], "utf-8")

            # if ctype == 'multipart/form-data':
            #     fields = cgi.parse_multipart(self.rfile, pdict)
            #     messagecontent = fields.get('message')

            # output = ""
            # output += "<html><body>"
            # output += " <h2> Okay, how about this: </h2>"
            # output += "<h1> {} </h1>".format(messagecontent[0].decode())
            # output += self.form_html
            # output += "</body></html>"
            # self.wfile.write(output.encode())
            # print(output)

        except:
            raise


def main():
    try:
        port = 8080
        server = HTTPServer(('', port), WebServerHandler)
        print("Web server is running on port {}".format(port))
        server.serve_forever()

    except KeyboardInterrupt:
        print("^C entered, stopping web server...")

    finally:
        if server:
            server.socket.close()


if __name__ == '__main__':
    main()