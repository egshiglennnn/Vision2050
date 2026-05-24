# PDF Sources — Direct Download Links

Save each PDF to `data/pdfs/` with the filename shown.

| Code | Filename | Country | Plan | Download URL |
|------|----------|---------|------|--------------|
| RWA | RWA.pdf | Rwanda | Vision 2050 | https://www.minecofin.gov.rw/fileadmin/user_upload/Minecofin/Publications/REPORTS/National_Development_Planning_and_Research/Vision_2050/English-Vision_2050_Abridged_version_WEB_Final.pdf |
| GHA | GHA.pdf | Ghana | Ghana Beyond Aid | https://www.ndpc.gov.gh/GPRS/Ghana_Beyond_Aid_Charter_and_Strategy_Document.pdf |
| PAK | PAK.pdf | Pakistan | Vision 2025 | https://pc.gov.pk/uploads/vision2025/Pakistan-Vision-2025.pdf |
| KEN | KEN.pdf | Kenya | Vision 2030 | https://vision2030.go.ke/wp-content/uploads/2018/05/Vision-2030-Popular-Version.pdf |
| NGA | NGA.pdf | Nigeria | Agenda 2050 | https://nationalplanning.gov.ng/wp-content/uploads/2021/12/Nigeria-Agenda-2050-1.pdf |
| BGD | BGD.pdf | Bangladesh | Perspective Plan 2041 | https://www.plancomm.gov.bd/site/files/5f34e31e-1cca-45c4-9df0-c8a6aaf3aedb/Perspective-Plan-of-Bangladesh-2021-2041 |
| IND | IND.pdf | India | Vision India@2047 | https://www.niti.gov.in/sites/default/files/2023-09/Vision-India-at-2047.pdf |
| ETH | ETH.pdf | Ethiopia | Ten Year Dev. Plan 2030 | https://www.undp.org/sites/g/files/zskgke326/files/migration/et/UNDP-Ethiopia-Ten-Year-Development-Plan.pdf |
| TZA | TZA.pdf | Tanzania | Dev. Vision 2050 | https://www.mof.go.tz/docs/Tanzania_Development_Vision_2050.pdf |
| MYS | MYS.pdf | Malaysia | Shared Prosperity Vision 2030 | https://www.pmo.gov.my/wp-content/uploads/2019/10/Wawasan-Kemakmuran-Bersama-2030.pdf |
| MNG | MNG.pdf | Mongolia | Vision 2050 | https://mlsp.gov.mn/content/files/Mongolia%20Vision%202050.pdf |

## Bulk Download Script

```bash
# Run from project root
mkdir -p data/pdfs
cd data/pdfs

curl -L -o RWA.pdf "https://www.minecofin.gov.rw/fileadmin/user_upload/Minecofin/Publications/REPORTS/National_Development_Planning_and_Research/Vision_2050/English-Vision_2050_Abridged_version_WEB_Final.pdf"
curl -L -o GHA.pdf "https://www.ndpc.gov.gh/GPRS/Ghana_Beyond_Aid_Charter_and_Strategy_Document.pdf"
curl -L -o PAK.pdf "https://pc.gov.pk/uploads/vision2025/Pakistan-Vision-2025.pdf"
curl -L -o KEN.pdf "https://vision2030.go.ke/wp-content/uploads/2018/05/Vision-2030-Popular-Version.pdf"
curl -L -o NGA.pdf "https://nationalplanning.gov.ng/wp-content/uploads/2021/12/Nigeria-Agenda-2050-1.pdf"
curl -L -o BGD.pdf "https://www.plancomm.gov.bd/site/files/5f34e31e-1cca-45c4-9df0-c8a6aaf3aedb/Perspective-Plan-of-Bangladesh-2021-2041"
curl -L -o IND.pdf "https://www.niti.gov.in/sites/default/files/2023-09/Vision-India-at-2047.pdf"
curl -L -o ETH.pdf "https://www.undp.org/sites/g/files/zskgke326/files/migration/et/UNDP-Ethiopia-Ten-Year-Development-Plan.pdf"
curl -L -o TZA.pdf "https://www.mof.go.tz/docs/Tanzania_Development_Vision_2050.pdf"
curl -L -o MYS.pdf "https://www.pmo.gov.my/wp-content/uploads/2019/10/Wawasan-Kemakmuran-Bersama-2030.pdf"
curl -L -o MNG.pdf "https://mlsp.gov.mn/content/files/Mongolia%20Vision%202050.pdf"

echo "Done. Check file sizes:"
ls -lh *.pdf
```

## Notes
- Some URLs may redirect — use `curl -L` (follow redirects)
- If a URL is broken, search "[Country] [Plan Name] PDF" on the ministry/planning commission website
- Fallback for Ghana: https://ndpc.gov.gh
- Fallback for Mongolia: https://legalinfo.mn or UN Development Programme Mongolia office
- All documents are publicly available government publications
