from utils import verify_tree_positions, plot_centroid_variants_from_index


txt_path = r"arbeitspakete\02_segmentierung\01_Segm_Bäume\input\PW_Baeume_o_Boden.txt"
csv_path = r"arbeitspakete\02_segmentierung\01_Segm_Bäume\output\baumdaten_watershed.csv"

verify_tree_positions(txt_path, csv_path)

# plot_centroid_variants_from_index(txt_path, csv_path, res=0.5)