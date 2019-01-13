#include <unistd.h>
#include <sys/types.h>
#include <pwd.h>
#include "time.h"
#include "fly_storm.h" 
#include "propagator.h" 
#include "moat_prototype.h"
#include "options.h"

int nProcs;
int iProc;

/////////////////////////////////////////////////////////////////////////////////////////
//
//  Name:           convert_find_specular_output_from_bin_to_txt
//  Purpose:        Convert the binary file(s) generated by find_specular_points.c into txt files
//  Assumptions:    None
//  References      None
//
//  Change Log:
//      |   Developer   |       Date    |   SCR     |   Notes
//      | --------------|---------------|-----------|-------------------------------
//      | C. Bussy-Virat| 10/01/2015    |   ---     | Initial implementation
//
/////////////////////////////////////////////////////////////////////////////////////////
int convert_find_specular_output_from_bin_to_txt( OPTIONS_T *OPTIONS,   char filename_storm_interpolated[100][N_STORM], int iCygnss, int compute_coverage)
{
  // Declarations
  char *next_interpolated;
  int find_file_name;
  int ierr;
  int ss;
  OPTIONS_T       OPTIONS;
  PARAMS_T        PARAMS;
  char filename_input[256];
  char filename_storm_interpolated[100][N_STORM];
  char main_directory_location[256];    
  int iDebugLevel = -1; // for now set it to 0
  /* Create child processes, each of which has its own variables.
   * From this point on, every process executes a separate copy
   * of this program.  Each process has a different process ID,
   * ranging from 0 to nProcs minus 1, and COPIES of all
   * variables defined in the program. No variables are shared.
   **/
  int specular_on_storm ;
  double lat_storm, lon_storm, storm_radius_uncertainty;
  double ecef_x_storm, ecef_y_storm, ecef_z_storm;
  double et_storm;
  char time_storm[256];
  char *line = NULL;
  size_t len = 0;
  double distance_specular_point_to_center_of_storm;
  FILE *file_storm_interpolated;
  FILE *file_specular_position_in;
  char filename_specular_position_in[256];
  char filename_specular_position_out[256];
  FILE *file_specular_position_out;


  ierr = MPI_Init(&argc, &argv);
     
  /* find out MY process ID, and how many processes were started. */
      
  ierr = MPI_Comm_rank(MPI_COMM_WORLD, &iProc);
  ierr = MPI_Comm_size(MPI_COMM_WORLD, &nProcs);

  //  Load Options
  strcpy(filename_input, "./input/main_input/");
  strcat(filename_input, argv[1]);
  strcpy(main_directory_location, "./");
  load_options( &OPTIONS, filename_input, nProcs, main_directory_location, iDebugLevel);

  // Load Params
  load_params( &PARAMS, main_directory_location );

  /* Algorithm */
  // read specular file
  int iStart, iEnd, nCygEachPe, nCygLeft,i, iCygnss;
  nCygEachPe = (OPTIONS->n_satellites - OPTIONS->nb_gps)/nProcs;
  nCygLeft = (OPTIONS->n_satellites - OPTIONS->nb_gps) - (nCygEachPe * nProcs);
  iStart = 0;
  for (i=0; i<iProc; i++) {
    iStart += nCygEachPe;
    if (i < nCygLeft && iProc > 0) iStart++;
  }
  iEnd = iStart+nCygEachPe;
  if (iProc < nCygLeft) iEnd++;
  for (iCygnss=iStart; iCygnss<iEnd; iCygnss++) {

  strcpy(filename_specular_position_in, OPTIONS->dir_output_run_name_sat_name[iCygnss]);
  strcat(filename_specular_position_in, "/specular_");
  char *next; int find_file_name;      char sat_name[256];
  next = &OPTIONS->filename_output[iCygnss][0];
  find_file_name =  (int)(strchr(next, '.') - next);
  strncat(filename_specular_position_in, next, find_file_name);
  strcat(filename_specular_position_in, ".bin");
  file_specular_position_in = fopen(filename_specular_position_in, "r");

  // create output file 
    strcpy(filename_specular_position_out, OPTIONS->dir_output_run_name_sat_name[iCygnss]);
    strcat(filename_specular_position_out, "/specular_");
    strncat(filename_specular_position_out, next, find_file_name);
    strcpy(sat_name, "");
    strncat(sat_name, next, find_file_name);
    strcat(filename_specular_position_out, ".txt");
    file_specular_position_out = fopen(filename_specular_position_out, "w+");
    fprintf(file_specular_position_out, "This file shows the positions of the specular points for %s. Every 60 seconds, it also shows the positions and the velocity of the GPS and %s.\nNote: there is also the possibility of calculating the distance from each specular point to a storm.\nTIME ECEF_SPEC_X ECEF_SPEC_Y ECEF_SPEC_Z LON_SPEC LAT_SPEC GAIN NAME_GPS ECEF_GPS_X ECEF_GPS_Y ECEF_GPS_Z ECEF_GPS_VX ECEF_GPS_VY ECEF_GPS_VZ ECEF_CYGNSS_X ECEF_CYGNSS_Y ECEF_CYGNSS_Z ECEF_CYGNSS_VX ECEF_CYGNSS_VY ECEF_CYGNSS_VZ\n#START\n", sat_name, sat_name);

  // Read the bin file created by find_specular_points.c
  int iGps, iPt;
    int iPtInner;
    float lon_spec, lat_spec, gain_spec, ecef_x_spec, ecef_y_spec, ecef_z_spec, time_ymdhmsm[7]; 
    int sss;
    char year_str[15], month_str[15], day_str[15], hour_str[15], minute_str[15], second_str[15], time_str[120];
    double et_spec, et_spec_save; char time_spec[256];

  while(!feof(file_specular_position_in)){

    fread(&iGps,sizeof(iGps),1,file_specular_position_in);
    fread(&iPt,sizeof(iPt),1,file_specular_position_in);
    iPtInner = ( iPt % (int) (OPTIONS->dt) );
    if (iPtInner == 0){
      for (sss = 0; sss < 7; sss ++){
	fread(&time_ymdhmsm[sss],sizeof(time_ymdhmsm[sss]),1,file_specular_position_in);
      }
      sprintf(year_str, "%d", (int)(time_ymdhmsm[0]));
      sprintf(month_str, "%d", (int)(time_ymdhmsm[1]));
      sprintf(day_str, "%d", (int)(time_ymdhmsm[2]));
      sprintf(hour_str, "%d", (int)(time_ymdhmsm[3]));
      sprintf(minute_str, "%d", (int)(time_ymdhmsm[4]));
      sprintf(second_str, "%d", (int)(time_ymdhmsm[5]));
      strcpy(time_str, "");
      strcat(time_str, year_str); strcat(time_str, "-"); strcat(time_str, month_str); strcat(time_str, "-"); strcat(time_str, day_str); strcat(time_str, "T"); strcat(time_str, hour_str); strcat(time_str, ":"); strcat(time_str, minute_str); strcat(time_str, ":"); strcat(time_str, second_str);
      str2et_c(time_str, &et_spec);
      et_spec_save = et_spec;
    }
    else{
      et_spec = et_spec_save + iPtInner; // iPtInner always increments by one second in find_specular_points.c
    }

    et2utc_c(et_spec, "ISOC" ,0 ,255 , time_spec);
    fread(&ecef_x_spec,sizeof(ecef_x_spec),1,file_specular_position_in);
    fread(&ecef_y_spec,sizeof(ecef_y_spec),1,file_specular_position_in);
    fread(&ecef_z_spec,sizeof(ecef_z_spec),1,file_specular_position_in);

    // !!!!!!!!!!!!!!!! COMMENT THESE LINES BELOW!
    /* float ecef_x_gps, ecef_y_gps, ecef_z_gps, ecef_x_sat, ecef_y_sat, ecef_z_sat; */
    /* fread(&ecef_x_gps,sizeof(ecef_x_gps),1,file_specular_position_in); */
    /* fread(&ecef_y_gps,sizeof(ecef_y_gps),1,file_specular_position_in); */
    /* fread(&ecef_z_gps,sizeof(ecef_z_gps),1,file_specular_position_in); */
    /* fread(&ecef_x_sat,sizeof(ecef_x_sat),1,file_specular_position_in); */
    /* fread(&ecef_y_sat,sizeof(ecef_y_sat),1,file_specular_position_in); */
    /* fread(&ecef_z_sat,sizeof(ecef_z_sat),1,file_specular_position_in); */
    // !!!!!!!!!!!!!!!! END OF COMMENT THESE LINES BELOW!

    fread(&lon_spec,sizeof(lon_spec),1,file_specular_position_in);
    fread(&lat_spec,sizeof(lat_spec),1,file_specular_position_in);
    fread(&gain_spec,sizeof(gain_spec),1,file_specular_position_in);

    if (!feof(file_specular_position_in)){
      fprintf(file_specular_position_out, "%s %f %f %f %f %f %f %s", time_spec, ecef_x_spec, ecef_y_spec, ecef_z_spec, lon_spec, lat_spec, gain_spec, OPTIONS->gps_file_name[iGps]);
    }

    // !!!!!!!!!!!!!!!! COMMENT THESE LINES BELOW!
    float ecef_x_gps, ecef_y_gps, ecef_z_gps, ecef_x_sat, ecef_y_sat, ecef_z_sat,ecef_vx_gps, ecef_vy_gps, ecef_vz_gps, ecef_vx_sat, ecef_vy_sat, ecef_vz_sat;
    //  if ( iPt % 60 == 0 ){
      fread(&ecef_x_gps,sizeof(ecef_x_gps),1,file_specular_position_in);
      fread(&ecef_y_gps,sizeof(ecef_y_gps),1,file_specular_position_in);
      fread(&ecef_z_gps,sizeof(ecef_z_gps),1,file_specular_position_in);
      fread(&ecef_vx_gps,sizeof(ecef_x_gps),1,file_specular_position_in);
      fread(&ecef_vy_gps,sizeof(ecef_y_gps),1,file_specular_position_in);
      fread(&ecef_vz_gps,sizeof(ecef_z_gps),1,file_specular_position_in);
      fread(&ecef_x_sat,sizeof(ecef_x_sat),1,file_specular_position_in);
      fread(&ecef_y_sat,sizeof(ecef_y_sat),1,file_specular_position_in);
      fread(&ecef_z_sat,sizeof(ecef_z_sat),1,file_specular_position_in);
      fread(&ecef_vx_sat,sizeof(ecef_x_sat),1,file_specular_position_in);
      fread(&ecef_vy_sat,sizeof(ecef_y_sat),1,file_specular_position_in);
      fread(&ecef_vz_sat,sizeof(ecef_z_sat),1,file_specular_position_in);

      if (!feof(file_specular_position_in)){
    	fprintf(file_specular_position_out, " %f %f %f %f %f %f %f %f %f %f %f %f", ecef_x_gps, ecef_y_gps, ecef_z_gps,ecef_vx_gps, ecef_vy_gps, ecef_vz_gps, ecef_x_sat, ecef_y_sat, ecef_z_sat,ecef_vx_sat, ecef_vy_sat, ecef_vz_sat);
      }
      ///}
    // !!!!!!!!!!!!!!!! END OF COMMENT THESE LINES BELOW!


    // !!!!!!!!!!!!!!!! COMMENT THESE LINES BELOW! these are just when I want to look at the positions of the specular points with respect to the CYGNSS and GPS satellites
    /* if (!feof(file_specular_position_in)){ */
    /*   fprintf(file_specular_position_out, "%s %f %f %f %f %f %f %f %f %f", time_spec, ecef_x_spec, ecef_y_spec, ecef_z_spec, ecef_x_gps, ecef_y_gps, ecef_z_gps, ecef_x_sat, ecef_y_sat, ecef_z_sat); */
    /* } */
    // !!!!!!!!!!!!!!!! END OF COMMENT THESE LINES BELOW!

    if ( compute_coverage == 1 ){
      et2utc_c(et_spec, "ISOC" ,0 ,255 , time_spec);
      et2utc_c(et_storm, "ISOC" ,0 ,255 , time_storm);

      // compute the coverage of the specular points in the storm
      if (et_storm - 0.00001 <= et_spec){ // - 0.00001 is just here for some numerical reasons
	while (et_storm + 0.0000001< et_spec){
	  getline(&line,&len,file_storm_interpolated);
	  sscanf(line, "%19[^\n] %lf %lf %lf %lf %lf %lf", time_storm, &lat_storm, &lon_storm, &ecef_x_storm, &ecef_y_storm, &ecef_z_storm, &storm_radius_uncertainty);
	  str2et_c(time_storm, &et_storm);	  
	}
     
	distance_specular_point_to_center_of_storm = sqrt( ( ecef_x_spec - ecef_x_storm ) * ( ecef_x_spec - ecef_x_storm  )  +  ( ecef_y_spec - ecef_y_storm ) * ( ecef_y_spec - ecef_y_storm  ) +  ( ecef_z_spec - ecef_z_storm ) * ( ecef_z_spec - ecef_z_storm ) ) ;
	if ( distance_specular_point_to_center_of_storm <= storm_radius_uncertainty ){
	  specular_on_storm = 1;
	}
	else{
	  specular_on_storm = 0;
	}
    if (!feof(file_specular_position_in)){
	fprintf(file_specular_position_out, " %f %d\n", distance_specular_point_to_center_of_storm, specular_on_storm);
    }
      }
      else{
    if (!feof(file_specular_position_in)){
	fprintf(file_specular_position_out, " NO_DATA NO_DATA\n");
    }
      }
    }
    else{
      fprintf(file_specular_position_out,"\n");
    }
  }

  fclose(file_specular_position_in);
  fclose(file_specular_position_out); 

  }

  /* // Notify Exit */
  if (iProc == 0) {
    printf("Done converting the specular points output binary files into txt files.\n");
  }

  ierr = MPI_Finalize();    

  return 0;

}

