# -*-coding=utf-8-*-

import os
import sys
import glob
import subprocess
import configparser
from copy import deepcopy

from mRNA_report_interface import three_line_table,find_sample_file,create_template,create_mRNA_dir_map,create_mRNA_file_map
template_dir = '/home/lxgui/chencheng/report/latex2pdf'

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print 'python + {argv} + mRNA_report_dir'.format(argv=sys.argv[0])
        sys.exit(1)

    mRNA_report_dir = os.path.abspath(sys.argv[1])
    replace_dir = os.path.dirname(mRNA_report_dir)

    command = configparser.ConfigParser()
    command.read('report_conf.conf')
    report_name = command.get('mRNA', 'report_name')
    project_name = command.get('mRNA', 'project_name')
    assembly = command.get('mRNA', 'assembly')

    mRNA_report_file_info = create_mRNA_file_map(mRNA_report_dir)
    mRNA_report_dir_info = create_mRNA_dir_map(mRNA_report_dir)
    assembly_files = (mRNA_report_file_info['Trinity_stat_txt'],
                      mRNA_report_file_info['Isoform_length_distribution'],
                      mRNA_report_file_info['Gene_length_distribution'])
    if assembly:
        for each in assembly_files:
            if not os.path.exists(each):
                print '{file} is not exists in assembly dir'.format(file=each)
                sys.exit(1)

    for key,value in mRNA_report_file_info.items():
        if not os.path.exists(value) and value not in assembly_files:
            print '{file} is not exists in report dir'.format(file=key)
            sys.exit(1)

    for key,value in mRNA_report_dir_info.items():
        if value == None:
            print '{dir} is not exists in report dir'.format(dir=key)
            sys.exit(1)

    #for create temp table
    template_table_dir = 'templates/data_table'
    three_line_table(mRNA_report_file_info['qc_summary_txt'],os.path.join(template_table_dir,'01mRNA_qc_data.txt'),split='\t',colunms=6)
    three_line_table(mRNA_report_file_info['Trinity_stat_txt'],os.path.join(template_table_dir,'Trinity_stat.txt'),split='\t',colunms=3)
    three_line_table(mRNA_report_file_info['Gene_tmp_xls'],os.path.join(template_table_dir,'02mRNA_gene_count.txt'),split='\t',colunms=6)
    three_line_table(find_sample_file(mRNA_report_dir_info['difftable_dir'],pattern='*results.txt'),
                 os.path.join(template_table_dir,'03mRNA_diff_table.txt'),split='\t',colunms=5)
    three_line_table(find_sample_file(mRNA_report_dir_info['go_enrichtable_dir'],pattern='*ALL.GO.enrich.xls'),
                 os.path.join(template_table_dir,'04mRNA_GO_enrichment_table.txt'),split='\t',colunms=7)
    three_line_table(find_sample_file(mRNA_report_dir_info['kegg_enrichtable_dir'],pattern='*ALL.KEGG.enrich.xls'),
                 os.path.join(template_table_dir,'05mRNA_KEGG_enrichment_table.txt'),split='\t',colunms=7)
    
    mRNA_report_file_info_cp = deepcopy(mRNA_report_file_info)
    mRNA_report_dir_info_cp = deepcopy(mRNA_report_dir_info)

    for key,value in mRNA_report_file_info_cp.items():
        mRNA_report_file_info_cp[key] = value.replace(replace_dir,'')

    for key,value in mRNA_report_dir_info_cp.items():
        mRNA_report_dir_info_cp[key] = value.replace(replace_dir,'')
    
    context = {'project_name': project_name,
           'assembly':assembly,
           'report_name': report_name,
           'Isoform_length_plot':'{.' + mRNA_report_file_info_cp['Isoform_length_distribution'] + '}',
	   'Gene_length_plot': '{.' + mRNA_report_file_info_cp['Gene_length_distribution']+ '}',
           'all_quality_data_barplot_01': '{.' + mRNA_report_file_info_cp['all_quality_data_barplot'] + '}',
           'Gene_merge_plot_02': '{./' + mRNA_report_file_info_cp['Gene_expression_plot'] + '}',
           'sample_correlation_plot_03': '{.' + mRNA_report_file_info_cp['sample_correlation_plot'] + '}',
           'PCA_plot_04': '{.' + mRNA_report_file_info_cp['PCA_plot'] + '}',
           'diff_table_href': '{run:.' + mRNA_report_dir_info_cp['difftable_dir'] + '}',
           'volcano_plot_05': '{.' + mRNA_report_file_info_cp['volcano_example_plot'] + '}',
           'volcano_plot_href': '{run:.' + mRNA_report_dir_info_cp['volcano_plot_dir'] + '}',
           'heatmap_plot_06': '{.' + os.path.join(mRNA_report_dir_info_cp['heatmap_dir'],'Heatmap.png') + '}',
           'cluster_plot_07': '{.' + mRNA_report_file_info_cp['cluster_example_plot'] + '}',
           'heatmap_plot_href': '{run:.' + mRNA_report_dir_info_cp['heatmap_dir'] + '}',
           'GO_enrichment_table_href': '{run:.' + mRNA_report_dir_info_cp['go_enrichtable_dir'] + '}',
           'GO_barplot_08': '{.' + mRNA_report_file_info_cp['GO_example_plot'] + '}',
           'GO_barplot_href': '{run:.' + mRNA_report_dir_info_cp['go_barplot_dir'] + '}',
           'GO_dagplot_BP': '{.' + find_sample_file(mRNA_report_dir_info['go_dagplot_dir'], pattern='ALL.BP.GO.DAG.png').replace(replace_dir,'') + '}',
           'GO_dagplot_CC': '{.' + find_sample_file(mRNA_report_dir_info['go_dagplot_dir'], pattern='ALL.CC.GO.DAG.png').replace(replace_dir,'') + '}',
           'GO_dagplot_MF': '{.' + find_sample_file(mRNA_report_dir_info['go_dagplot_dir'], pattern='ALL.MF.GO.DAG.png').replace(replace_dir,'') + '}',
           'GO_dagplot_href': '{run:.' + mRNA_report_dir_info_cp['go_dagplot_dir'] + '}',
           'KEGG_enrichment_table_href': '{run:.' + mRNA_report_dir_info_cp['kegg_enrichtable_dir'] + '}',
           'KEGG_barplot_09': '{.' + mRNA_report_file_info_cp['KEGG_example_plot'] + '}',
           'KEGG_barplot_href': '{run:.' + mRNA_report_dir_info_cp['kegg_barplot_dir'] + '}',
           'KEGG_pathway1': '{.' + find_sample_file(mRNA_report_dir_info['kegg_pathway_dir'], pattern='ALL_pathway')[0].replace(replace_dir,'') + '}',
           'KEGG_pathway2': '{.' + find_sample_file(mRNA_report_dir_info['kegg_pathway_dir'], pattern='ALL_pathway')[1].replace(replace_dir,'') + '}',
           'KEGG_pathway3': '{.' + find_sample_file(mRNA_report_dir_info['kegg_pathway_dir'], pattern='ALL_pathway')[2].replace(replace_dir,'') + '}',
           'KEGG_pathway_href': '{run:.' + mRNA_report_dir_info_cp['kegg_pathway_dir'] + '}'
           }
    output_tex_file = 'mRNA_analysis_report.tex'
    REPORT_DIR_SHORT = os.path.dirname(mRNA_report_dir)
    create_template('mRNA_main.txt', os.path.join(REPORT_DIR_SHORT, output_tex_file), context)
    # run xelatex:
    ref_file = os.path.join(template_dir, 'templates/mRNA_report/') + 'ref.bib'
    os.chdir(REPORT_DIR_SHORT)
    output_aux_file = output_tex_file.replace('tex', 'aux')
    tex_list = glob.glob(os.path.join(REPORT_DIR_SHORT, output_tex_file))
    rm_set = ('.aux', '.log', '.out', '.toc', '.tex', '.tmp', '.bib', '.bbl', '.blg')

    if len(tex_list) == 1:
        subprocess.call('cp %s ./' % ref_file, shell=True)
        subprocess.call('xelatex %s' % output_tex_file, shell=True)
        subprocess.call('bibtex %s' % output_aux_file, shell=True)
        subprocess.call('xelatex %s' % output_tex_file, shell=True)
        subprocess.call('xelatex %s' % output_tex_file, shell=True)
        for each_file in os.listdir(REPORT_DIR_SHORT):
            if os.path.splitext(each_file)[1] in rm_set:
                subprocess.call('rm %s' % each_file, shell=True)
    else:
        print 'Not one tex file in {dir}!'.format(dir=REPORT_DIR_SHORT)
        sys.exit(1)

    subprocess.call('echo mRNA report done!', shell=True)












