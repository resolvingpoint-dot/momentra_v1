# Native client loading-optimization sources (reference)

Android (`apk_copy/`) and iOS (`ios_copy/`) are not yet published on `origin` as first-class trees.
These files are **copies of the implemented loading paths** for PR review:

- Business Action Center: schema-versioned catalog cache + skip `/renderer` when `fields` embedded
- Master Expense: options `CachedFetcher` / peek → background revalidate

Apply back into the shipping Android/iOS packages before release. Web + backend changes in this PR are authoritative for those platforms.
