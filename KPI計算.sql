WITH
  kessai AS (
    SELECT
      t1.kessai_month,
      t1.user_id,
      t2.nendai,
      t2.gender,
      SUM(t1.kessai_amount) AS kessai_amount,
      SUM(t1.kessai_count) AS kessai_count
    FROM
      kessai_table t1
    LEFT JOIN
      user_table t2
    ON
      t1.user_id = t2.user_id
    GROUP BY
      t1.kessai_month,
      t1.user_id,
      t2.nendai,
      t2.gender
  ),
  -- 基本統計
  basic_stats AS (
    SELECT
      COUNT(DISTINCT user_id) AS uu_count,
      SUM(kessai_amount) AS total_kessai_amount,
      AVG(kessai_amount) AS avg_kessai_amount,
      AVG(kessai_count) AS avg_kessai_count
    FROM
      kessai
  ),
  -- 顧客単価（合計決済金額 / UU数）
  customer_value AS (
    SELECT
      SUM(kessai_amount) / COUNT(DISTINCT user_id) AS avg_customer_value
    FROM
      kessai
  ),
  -- 男女比
  gender_ratio AS (
    SELECT
      gender,
      COUNT(user_id) AS gender_count,
      COUNT(user_id) * 100.0 / (
        SELECT
          COUNT(DISTINCT user_id)
        FROM
          kessai
      ) AS gender_percentage
    FROM
      kessai
    WHERE
      gender IS NOT NULL
    GROUP BY
      gender
  ),
  -- 年代別割合
  age_group_ratio AS (
    SELECT
      nendai,
      COUNT(user_id) AS age_count,
      COUNT(user_id) * 100.0 / (
        SELECT
          COUNT(DISTINCT user_id)
        FROM
          kessai
      ) AS age_percentage
    FROM
      kessai
    WHERE
      nendai IS NOT NULL
    GROUP BY
      nendai
    ORDER BY
      nendai
  )
SELECT
  -- 基本統計
  bs.uu_count,
  bs.total_kessai_amount,
  bs.avg_kessai_amount,
  bs.avg_kessai_count,
  -- 顧客単価
  cv.avg_customer_value,
  -- 男女比
  (
    SELECT
      STRING_AGG (
        gender || ':' || ROUND(gender_percentage, 2) || '%',
        ', '
        ORDER BY
          gender
      )
    FROM
      gender_ratio
  ) AS gender_distribution,
  -- 年代別割合
  (
    SELECT
      STRING_AGG (
        nendai || ':' || ROUND(age_percentage, 2) || '%',
        ', '
        ORDER BY
          nendai
      )
    FROM
      age_group_ratio
  ) AS age_distribution
FROM
  basic_stats bs,
  customer_value cv
;
