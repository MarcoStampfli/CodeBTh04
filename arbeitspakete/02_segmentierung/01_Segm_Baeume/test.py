from utils import verify_tree_positions, plot_centroid_variants_from_index


txt_path = r"arbeitspakete\02_segmentierung\01_Segm_Bäume\input\PW_Baeume_o_Boden_o_Rauschen.txt"
csv_path = r"arbeitspakete\02_segmentierung\01_Segm_Bäume\output\baumdaten_watershed_RunID_202504272_Parameter_res1_minPix3_sig1_minH1.5_eps3_minSam150_DM2.5bis11.csv"

verify_tree_positions(txt_path, csv_path)

# plot_centroid_variants_from_index(txt_path, csv_path, res=0.5)

