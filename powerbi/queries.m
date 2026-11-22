// =============================================================================
// Power Query (M Code) Data Transformations for Power BI
// Capstone-I, Group 03, IIT Patna
// Author: Md. Adnan
// =============================================================================

// How to use in Power BI Desktop:
// 1. Go to "Transform data" (opens Power Query Editor).
// 2. Select "New Source" > "Blank Query".
// 3. Click "Advanced Editor" in the ribbon.
// 4. Paste each query block below and rename the query as indicated.
// 5. Replace the "FolderPath" parameter with your local repo path if different.


// -----------------------------------------------------------------------------
// PARAMETER: FolderPath
// Create a new parameter named FolderPath (Type: Text)
// -----------------------------------------------------------------------------
"C:\Users\ADNAN\OneDrive\Projects\ott-capstone\data\processed\" meta [IsParameterQuery=true, Type="Text", IsParameterQueryRequired=true]


// -----------------------------------------------------------------------------
// TABLE 1: catalog_titles
// Source: data/processed/catalog_titles.csv
// -----------------------------------------------------------------------------
let
    Source = Csv.Document(File.Contents(FolderPath & "catalog_titles.csv"), [Delimiter=",", Columns=25, Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    #"Changed Types" = Table.TransformColumnTypes(#"Promoted Headers", {
        {"catalog_key", type text},
        {"platform", type text},
        {"type", type text},
        {"title", type text},
        {"release_year", Int64.Type},
        {"title_key", type text},
        {"title_missing", type logical},
        {"title_damaged", type logical},
        {"country_known", type logical},
        {"country_first", type text},
        {"origin_group", type text},
        {"india_any", type logical},
        {"us_any", type logical},
        {"age_rating_raw", type text},
        {"age_group", type text},
        {"age_order", Int64.Type},
        {"runtime_min", type number},
        {"seasons", Int64.Type},
        {"n_genre_groups", Int64.Type},
        {"release_period", type text},
        {"period_order", Int64.Type},
        {"decade", Int64.Type},
        {"on_both", type logical},
        {"director_known", type logical},
        {"cast_known", type logical}
    })
in
    #"Changed Types"


// -----------------------------------------------------------------------------
// TABLE 2: catalog_genre_groups
// Source: data/processed/catalog_genre_groups.csv
// -----------------------------------------------------------------------------
let
    Source = Csv.Document(File.Contents(FolderPath & "catalog_genre_groups.csv"), [Delimiter=",", Columns=4, Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    #"Changed Types" = Table.TransformColumnTypes(#"Promoted Headers", {
        {"catalog_key", type text},
        {"platform", type text},
        {"type", type text},
        {"genre_group", type text}
    })
in
    #"Changed Types"


// -----------------------------------------------------------------------------
// TABLE 3: imdb_titles
// Source: data/processed/titles.csv
// -----------------------------------------------------------------------------
let
    Source = Csv.Document(File.Contents(FolderPath & "titles.csv"), [Delimiter=",", Columns=9, Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    #"Changed Types" = Table.TransformColumnTypes(#"Promoted Headers", {
        {"title_key", type text},
        {"platform", type text},
        {"title", type text},
        {"year", Int64.Type},
        {"imdb", type number},
        {"rt", type number},
        {"age_rating", type text},
        {"release_period", type text},
        {"period_order", Int64.Type}
    }),
    #"Added Link Column" = Table.AddColumn(#"Changed Types", "link", each [platform] & "|" & [title_key], type text)
in
    #"Added Link Column"


// -----------------------------------------------------------------------------
// TABLE 4: imdb_genres
// Source: data/processed/genres.csv
// -----------------------------------------------------------------------------
let
    Source = Csv.Document(File.Contents(FolderPath & "genres.csv"), [Delimiter=",", Columns=3, Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    #"Changed Types" = Table.TransformColumnTypes(#"Promoted Headers", {
        {"title_key", type text},
        {"platform", type text},
        {"genre", type text}
    }),
    #"Added Link Column" = Table.AddColumn(#"Changed Types", "link", each [platform] & "|" & [title_key], type text)
in
    #"Added Link Column"
