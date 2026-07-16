from pyspark.sql import SparkSession
from pyspark.sql.functions import col, current_timestamp, to_date

INPUT_PATH = "/home/bigdata/Desktop/processed_zone/*"
OUTPUT_PATH = "/home/bigdata/Desktop/clean_data"

def main():
    spark = SparkSession.builder \
        .appName("BigDataPipeline-ProcessStage") \
        .getOrCreate()

    # قراءة الملفات اللي جابها Flume
    raw_df = spark.read.json(INPUT_PATH)

    print("=== Schema ===")
    raw_df.printSchema()

    print("=== Sample Data ===")
    raw_df.show(5, truncate=False)

    # تفكيك عمود data (اللي فيه الليستة الأصلية) وتنظيفه
    from pyspark.sql.functions import explode
    exploded_df = raw_df.select(explode(col("data")).alias("coin"))

    clean_df = exploded_df.select(
        col("coin.id").alias("id"),
        col("coin.symbol").alias("symbol"),
        col("coin.name").alias("name"),
        col("coin.current_price").alias("current_price"),
        col("coin.market_cap").alias("market_cap"),
        col("coin.total_volume").alias("total_volume"),
    ).dropna(subset=["id", "current_price"]) \
     .dropDuplicates(["id"]) \
     .withColumn("processed_at", current_timestamp())

    print(f"=== Clean records count: {clean_df.count()} ===")
    clean_df.show(10, truncate=False)

    # حفظ النتيجة كـ Parquet
    clean_df.write.mode("overwrite").parquet(OUTPUT_PATH)
    print(f"Saved clean data to {OUTPUT_PATH}")

    spark.stop()

if __name__ == "__main__":
    main()

