// cargar con mongo < productos.js o desde el shell con load("productos.js")
db.productos.drop();

db.productos.insertOne({'nombre':'iPad 16GB Wifi', 'fabricante':"Apple",
		    'categoria':'Tablets',
		    'precio':499.00});
db.productos.insertOne({'nombre':'iPad 32GB Wifi', 'categoria':'Tablets',
		    'fabricante':"Apple",
		    'precio':599.00});
db.productos.insertOne({'nombre':'iPad 64GB Wifi', 'categoria':'Tablets',
		    'fabricante':"Apple",
		    'precio':699.00});
db.productos.insertOne({'nombre':'Galaxy S3', 'categoria':'Smartphones',
		    'fabricante':'Samsung',
		    'precio':563.99});
db.productos.insertOne({'nombre':'Galaxy Tab 10', 'categoria':'Tablets',
		    'fabricante':'Samsung',
		    'precio':450.99});
db.productos.insertOne({'nombre':'Vaio', 'categoria':'Portátiles',
		    'fabricante':"Sony",
		    'precio':499.00});
db.productos.insertOne({'nombre':'Macbook Air 13inch', 'categoria':'Portátiles',
		    'fabricante':"Apple",
		    'precio':499.00});
db.productos.insertOne({'nombre':'Nexus 7', 'categoria':'Tablets',
		    'fabricante':"Google",
		    'precio':199.00});
db.productos.insertOne({'nombre':'Kindle Paper White', 'categoria':'Tablets',
		    'fabricante':"Amazon",
		    'precio':129.00});
db.productos.insertOne({'nombre':'Kindle Fire', 'categoria':'Tablets',
		    'fabricante':"Amazon",
		    'precio':199.00});