"""
Fixed version of the _measure_internal method 
"""


def _measure_internal(self):
    """
    Internal method that performs the actual measurement but doesn't return anything.
    This allows measure_2D to control when the file path is returned.
    """
    qkit.flow.start()
    try:
        """
        loop: x_obj with parameters from x_vec
        """
        for ix, x in enumerate(self.x_vec):
            self.x_set_obj(x)
            sleep(self.tdx)

            if self.log_function != None:
                for i, f in enumerate(self.log_function):
                    self._log_value[i].append(float(f(ix)))

            if self.log_function_2D != None:
                for i, f in enumerate(self.log_function_2D):
                    self._log_value_2D[i].append(f())

            if self._scan_dim == 3:
                for y in self.y_vec:
                    # loop: y_obj with parameters from y_vec (only 3D measurement)
                    if (
                        self.landscape.xylandscapes
                        and not self.landscape.perform_measurement_at_point(x, y, ix)
                    ):
                        # if point is not of interest (not close to one of the functions)
                        data_amp = np.full(int(self._nop), np.NaN, dtype=np.float16)
                        data_pha = np.full(
                            int(self._nop), np.NaN, dtype=np.float16
                        )  # fill with NaNs
                    else:
                        self.y_set_obj(y)
                        sleep(self.tdy)
                        if self.averaging_start_ready:
                            self.vna.start_measurement()
                            # Check if the VNA is STILL in ready state, then add some delay.
                            # If you manually decrease the poll_inveral, I guess you know what you are doing and will disable this safety query.
                            if self.vna_poll_interval >= 0.1 and self.vna.ready():
                                logging.debug("VNA STILL ready... Adding delay")
                                qkit.flow.sleep(
                                    0.2
                                )  # just to make sure, the ready command does not *still* show ready

                            while not self.vna.ready():
                                qkit.flow.sleep(
                                    min(
                                        self.vna.get_sweeptime_averages(query=False)
                                        / 11.0,
                                        self.vna_poll_interval,
                                    )
                                )
                        else:
                            self.vna.avg_clear()
                            qkit.flow.sleep(self._sweeptime_averages)

                        # if "avg_status" in self.vna.get_function_names():
                        #       while self.vna.avg_status() < self.vna.get_averages():
                        #            qkit.flow.sleep(.2) #maybe one would like to adjust this at a later point

                        """ measurement """
                        if not self.landscape.xzlandscape_func:  # normal scan
                            data_amp, data_pha = self.vna.get_tracedata()
                        else:
                            data_amp, data_pha = self.landscape.get_tracedata_xz(x)
                        if self.progress_bar:
                            self._p.iterate()

                    if self._nop == 0:  # this does not work yet.
                        print(data_amp[0], data_amp, self._nop)
                        self._data_amp.append(data_amp[0])
                        self._data_pha.append(data_pha[0])
                    else:
                        self._data_amp.append(data_amp)
                        self._data_pha.append(data_pha)
                    if self._fit_resonator:
                        self._do_fit_resonator()
                    qkit.flow.sleep()
                """
                filling of value-box is done here.
                after every y-loop the data is stored the next 2d structure
                """
                self._data_amp.next_matrix()
                self._data_pha.next_matrix()

            if self._scan_dim == 2:
                if self.averaging_start_ready:
                    self.vna.start_measurement()
                    if self.vna.ready():
                        logging.debug("VNA STILL ready... Adding delay")
                        qkit.flow.sleep(
                            0.2
                        )  # just to make sure, the ready command does not *still* show ready

                    while not self.vna.ready():
                        qkit.flow.sleep(
                            min(
                                self.vna.get_sweeptime_averages(query=False) / 11.0, 0.2
                            )
                        )
                else:
                    self.vna.avg_clear()
                    qkit.flow.sleep(self._sweeptime_averages)
                """ measurement """
                if not self.landscape.xzlandscape_func:  # normal scan
                    data_amp, data_pha = self.vna.get_tracedata()
                else:
                    data_amp, data_pha = self.landscape.get_tracedata_xz(x)

                data_pha = self.edel_correction_data(data_pha)
                self._data_amp.append(data_amp)
                self._data_pha.append(data_pha)

                if self._fit_resonator:
                    self._do_fit_resonator()
                if self.progress_bar:
                    self._p.iterate()
                qkit.flow.sleep()
    finally:
        # Just end the flow, don't end the measurement or return anything
        qkit.flow.end()


def _measure(self):
    """
    measures and plots the data depending on the measurement type.
    the measurement loops feature the setting of the objects and saving the data in the .h5 file.
    """
    # Call the internal measurement function
    self._measure_internal()

    # End the measurement and return the filepath
    file_path = self._end_measurement()

    return file_path  # return the filepath of the measurement file


def measure_2D(self, web_visible=True):
    """
    measure method to record a (averaged) VNA trace, S11 or S21 according to the setting on the VNA
    for all parameters x_vec in x_obj
    """

    if not self.x_set_obj:
        logging.error("axes parameters not properly set...aborting")
        return
    if (
        self.landscape.xzlandscape_func
    ):  # The vna limits need to be adjusted, happens in the frequency wrapper
        self.x_set_obj = self.landscape.vna_frequency_wrapper(self.x_set_obj)
    if len(self.x_vec) == 0:
        logging.error("No points to measure given. Check your x vector... aborting")
        return
    self._scan_dim = 2

    self._measurement_object.measurement_func = "measure_2D"
    self._measurement_object.x_axis = self.x_coordname
    self._measurement_object.y_axis = self.measurement_object_axis_name
    self._measurement_object.z_axis = ""
    self._measurement_object.web_visible = web_visible

    if not self.dirname:
        self.dirname = self.x_coordname
    self._file_name = "2D_" + self.dirname.replace(" ", "").replace(",", "_")
    if self.exp_name:
        self._file_name += "_" + self.exp_name

    if self.progress_bar:
        self._p = Progress_Bar(
            len(self.x_vec),
            "2D VNA sweep " + self.dirname,
            self.vna.get_sweeptime_averages(),
        )

    self._prepare_measurement_vna()
    self._prepare_measurement_file()

    """opens qviewkit to plot measurement, amp and pha are opened by default"""
    if self._nop < 10:
        self._data_file.hf.hf.attrs["default_ds"] = [
            "views/amplitude_midpoint",
            "views/phase_midpoint",
        ]
    else:
        self._data_file.hf.hf.attrs["default_ds"] = [
            "data0/amplitude_midpoint",
            "data0/phase_midpoint",
        ]

    if self.open_qviewkit:
        self._qvk_process = qviewkit.plot(
            self._data_file.get_filepath(),
            datasets=list(self._data_file.hf.hf.attrs["default_ds"]),
        )
    if self._fit_resonator:
        self._resonator = resonator(self._data_file.get_filepath())

    # Execute measurement and collect results
    self._measure_internal()

    # Return the filepath after all measurements are complete
    return self._data_file.get_filepath()
