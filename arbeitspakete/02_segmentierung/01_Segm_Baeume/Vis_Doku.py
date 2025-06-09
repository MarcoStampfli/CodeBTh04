from utils import verify_tree_positions2

# # Parameter von jeweiliger Run-ID
# datum = "20250517_2"
# output_dir = fr"arbeitspakete\02_segmentierung\01_Segm_Baeume\output\{datum}"
# csv_path= fr"{output_dir}\baumdaten_watershed_RunID_{datum}.csv"
# # PW von Bäume
# txt_path = r"arbeitspakete\02_segmentierung\01_Segm_Baeume\input\PW_Baeume_o_Boden_o_Rauschen.txt"
# # Output Filename
# filename = f"0_Doku_PW_vs_Kataster_Lauf_ID_3.png"


# verify_tree_positions2(output_dir=output_dir, csv_path=csv_path, txt_path=txt_path, filename=filename)

# Parameter von jeweiliger Run-ID
datum = "Baumdaten"
output_dir = fr"arbeitspakete\02_segmentierung\01_Segm_Baeume\output\{datum}"
csv_path= fr"{output_dir}\01_v3_baumdaten_watershed_merged.csv"
# PW von Bäume
txt_path = r"arbeitspakete\02_segmentierung\01_Segm_Baeume\input\PW_Baeume_o_Boden_o_Rauschen.txt"
# Output Filename
filename = f"0_Doku_PW_vs_Kataster_v3_merged.png"


verify_tree_positions2(output_dir=output_dir, csv_path=csv_path, txt_path=txt_path, filename=filename)