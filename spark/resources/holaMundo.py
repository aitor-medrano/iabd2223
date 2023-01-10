from pyspark.sql import SparkSession

spark = SparkSession.builder.getOrCreate()
sc = spark.sparkContext

# Suma de los 100 primeros números
rdd = sc.parallelize(range(100 + 1))
suma = rdd.sum()
print("--------------")
print(suma)
print("--------------")
