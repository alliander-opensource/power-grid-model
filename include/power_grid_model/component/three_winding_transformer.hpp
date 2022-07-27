// SPDX-FileCopyrightText: 2022 Contributors to the Power Grid Model project <dynamic.grid.calculation@alliander.com>
//
// SPDX-License-Identifier: MPL-2.0

#pragma once
#ifndef POWER_GRID_MODEL_COMPONENT_THREE_WINDING_TRANSFORMER_HPP
#define POWER_GRID_MODEL_COMPONENT_THREE_WINDING_TRANSFORMER_HPP

#include "branch3.hpp"
#include "transformer.hpp"

namespace power_grid_model {

class ThreeWindingTransformer : public Branch3 {
   public:
    using InputType = ThreeWindingTransformerInput;
    using UpdateType = ThreeWindingTransformerUpdate;
    static constexpr char const* name = "three_winding_transformer";

    ThreeWindingTransformer(ThreeWindingTransformerInput const& three_winding_transformer_input, double u1_rated,
                            double u2_rated, double u3_rated)
        : Branch3{three_winding_transformer_input},
          u1_{three_winding_transformer_input.u1},
          u2_{three_winding_transformer_input.u2},
          u3_{three_winding_transformer_input.u3},
          u1_rated_{u1_rated},
          u2_rated_{u2_rated},
          u3_rated_{u3_rated},
          sn_1_{three_winding_transformer_input.sn_1},
          sn_2_{three_winding_transformer_input.sn_2},
          sn_3_{three_winding_transformer_input.sn_3},
          uk_12_{three_winding_transformer_input.uk_12},
          uk_13_{three_winding_transformer_input.uk_13},
          uk_23_{three_winding_transformer_input.uk_23},
          pk_12_{three_winding_transformer_input.pk_12},
          pk_13_{three_winding_transformer_input.pk_13},
          pk_23_{three_winding_transformer_input.pk_23},
          i0_{three_winding_transformer_input.i0},
          p0_{three_winding_transformer_input.p0},
          winding_1_{three_winding_transformer_input.winding_1},
          winding_2_{three_winding_transformer_input.winding_2},
          winding_3_{three_winding_transformer_input.winding_3},
          clock_12_{three_winding_transformer_input.clock_12},
          clock_13_{three_winding_transformer_input.clock_13},
          tap_side_{three_winding_transformer_input.tap_side},
          tap_pos_{three_winding_transformer_input.tap_pos},
          tap_min_{three_winding_transformer_input.tap_min},
          tap_max_{three_winding_transformer_input.tap_max},
          tap_nom_{three_winding_transformer_input.tap_nom == na_IntS ? (IntS)0
                                                                      : three_winding_transformer_input.tap_nom},
          tap_direction_{tap_max_ > tap_min_ ? (IntS)1 : (IntS)-1},
          tap_size_{three_winding_transformer_input.tap_size},
          uk_12_min_{is_nan(three_winding_transformer_input.uk_12_min) ? uk_12_
                                                                       : three_winding_transformer_input.uk_12_min},
          uk_12_max_{is_nan(three_winding_transformer_input.uk_12_max) ? uk_12_
                                                                       : three_winding_transformer_input.uk_12_max},
          uk_13_min_{is_nan(three_winding_transformer_input.uk_13_min) ? uk_13_
                                                                       : three_winding_transformer_input.uk_13_min},
          uk_13_max_{is_nan(three_winding_transformer_input.uk_13_max) ? uk_13_
                                                                       : three_winding_transformer_input.uk_13_max},
          uk_23_min_{is_nan(three_winding_transformer_input.uk_23_min) ? uk_23_
                                                                       : three_winding_transformer_input.uk_23_min},
          uk_23_max_{is_nan(three_winding_transformer_input.uk_23_max) ? uk_23_
                                                                       : three_winding_transformer_input.uk_23_max},
          pk_12_min_{is_nan(three_winding_transformer_input.pk_12_min) ? pk_12_
                                                                       : three_winding_transformer_input.pk_12_min},
          pk_12_max_{is_nan(three_winding_transformer_input.pk_12_max) ? pk_12_
                                                                       : three_winding_transformer_input.pk_12_max},
          pk_13_min_{is_nan(three_winding_transformer_input.pk_13_min) ? pk_13_
                                                                       : three_winding_transformer_input.pk_13_min},
          pk_13_max_{is_nan(three_winding_transformer_input.pk_13_max) ? pk_13_
                                                                       : three_winding_transformer_input.pk_13_max},
          pk_23_min_{is_nan(three_winding_transformer_input.pk_23_min) ? pk_23_
                                                                       : three_winding_transformer_input.pk_23_min},
          pk_23_max_{is_nan(three_winding_transformer_input.pk_23_max) ? pk_23_
                                                                       : three_winding_transformer_input.pk_23_max},
          base_i_1_{base_power_3p / u1_rated / sqrt3},
          base_i_2_{base_power_3p / u2_rated / sqrt3},
          base_i_3_{base_power_3p / u3_rated / sqrt3},
          z_grounding_1_{calculate_z_pu(three_winding_transformer_input.r_grounding_1,
                                        three_winding_transformer_input.x_grounding_1, u1_rated)},
          z_grounding_2_{calculate_z_pu(three_winding_transformer_input.r_grounding_2,
                                        three_winding_transformer_input.x_grounding_2, u2_rated)},
          z_grounding_3_{calculate_z_pu(three_winding_transformer_input.r_grounding_3,
                                        three_winding_transformer_input.x_grounding_3, u3_rated)} {
        // TODO
    }

    // override getter
    double base_i_1() const final {
        return base_i_1_;
    }
    double base_i_2() const final {
        return base_i_2_;
    }
    double base_i_3() const final {
        return base_i_3_;
    }

    // setter
    bool set_tap(IntS new_tap) {
        if (new_tap == na_IntS || new_tap == tap_pos_) {
            return false;
        }
        tap_pos_ = tap_limit(new_tap);
        return true;
    }

    UpdateChange update(ThreeWindingTransformerUpdate const& update) {
        assert(update.id = id());
        bool topo_changed = set_status(update.status_1, update.status_2, update.status_3);
        bool param_changed = set_tap(update.tap_pos) || topo_changed;
        return {topo_changed, param_changed};
    }

   private:
    // three winding transformer parameters
    double u1_, u2_, u3_;
    double u1_rated_, u2_rated_, u3_rated_;
    double sn_1_, sn_2_, sn_3_;
    double uk_12_, uk_13_, uk_23_, pk_12_, pk_13_, pk_23_, i0_, p0_;
    WindingType winding_1_, winding_2_, winding_3_;
    IntS clock_12_, clock_13_;
    Branch3Side tap_side_;
    IntS tap_pos_, tap_min_, tap_max_, tap_nom_, tap_direction_;
    double tap_size_;
    double uk_12_min_, uk_12_max_, uk_13_min_, uk_13_max_, uk_23_min_, uk_23_max_;
    double pk_12_min_, pk_12_max_, pk_13_min_, pk_13_max_, pk_23_min_, pk_23_max_;

    // calculation parameters
    double base_i_1_;
    double base_i_2_;
    double base_i_3_;
    DoubleComplex z_grounding_1_;
    DoubleComplex z_grounding_2_;
    DoubleComplex z_grounding_3_;

    // calculate z in per unit with NaN detection
    DoubleComplex calculate_z_pu(double r, double x, double u) {
        r = is_nan(r) ? 0 : r;
        x = is_nan(x) ? 0 : x;
        double const base_z = u * u / base_power_3p;
        return {r / base_z, x / base_z};
    }

    IntS tap_limit(IntS new_tap) const {
        new_tap = std::min(new_tap, std::max(tap_max_, tap_min_));
        new_tap = std::max(new_tap, std::min(tap_max_, tap_min_));
        return new_tap;
    }

    std::tuple<double, double, double> calculate_uk() const {
        // convert all short circuit voltages relative to side 1
        double uk_12 = uk_12_ * sn_1_ / std::min(sn_1_, sn_2_);
        double uk_13 = uk_13_ * sn_1_ / std::min(sn_1_, sn_3_);
        double uk_23 = uk_23_ * sn_1_ / std : min(sn_2_, sn_3_);

        // delta-wye conversion (12, 13, 23 -> 1, 2, 3)
        double uk_T1_ = 0.5 * (uk_12 + uk_13 - uk_23);
        double uk_T2_ = 0.5 * (uk_12 + uk_23 - uk_13);
        double uk_T3_ = 0.5 * (uk_13 + uk_23 - uk_12);

        // transform short circuit voltages back to their own voltage level
        double uk_T1 = uk_T1_;
        double uk_T2 = uk_T2_ * (sn_2_ / sn_1_);
        double uk_T3 = uk_T3_ * (sn_3_ / sn_1_);
        return std::make_tuple(uk_T1, uk_T2, uk_T3);
    }

    std::tuple<double, double, double> calculate_pk() const {
        // convert all short circuit losses relative to side 1
        double pk_12 = pk_12_ * (sn_1_ / std::min(sn_1_, sn_2_)) * (sn_1_ / std::min(sn_1_, sn_2_));
        double pk_13 = pk_13_ * (sn_1_ / std::min(sn_1_, sn_3_)) * (sn_1_ / std::min(sn_1_, sn_3_));
        double pk_23 = pk_23_ * (sn_1_ / std::min(sn_2_, sn_3_)) * (sn_1_ / std::min(sn_2_, sn_3_));

        // delta-wye conversion (12, 13, 23 -> 1, 2, 3)
        double pk_T1_ = 0.5 * (pk_12 + pk_13 - pk_23);
        double pk_T2_ = 0.5 * (pk_12 + pk_23 - pk_13);
        double pk_T3_ = 0.5 * (pk_13 + pk_23 - pk_12);

        // transform short circuit losses back to their own power level
        double pk_T1 = pk_T1_;
        double pk_T2 = pk_T2_ * (sn_2_ / sn_1_) * (sn_2_ / sn_1_);
        double pk_T3 = pk_T3_ * (sn_3_ / sn_1_) * (sn_3_ / sn_1_);
        return std::make_tuple(pk_T1, pk_T2, pk_T3);
    }

    /*
    A three winding transformer can be modelled as three two winding transformers, between the three nodes and the
    dummy node:
        - T1: node 1 -> dummy node
        - T2: node 2 -> dummy node
        - T3: node 3 -> dummy node
    */
    std::tuple<Transformer, Transformer, Transformer> convert_to_two_winding_transformers() {
        const auto [transformer_input_T1, transformer_input_T2, transformer_input_T3] =
            get_two_winding_transformer_inputs();
        Transformer T1{transformer_input_T1, u1_rated_, u1_rated_};
        Transformer T2{transformer_input_T2, u2_rated_, u1_rated_};
        Transformer T3{transformer_input_T3, u3_rated_, u1_rated_};
    }

    /*
    The three two winding transformers look as follows:

                                node_2
                                 /
                                T2
                               /
    node_1 -- T1 -- dummy_node
                               \
                                T3
                                 \
                                node_3

    - Each two winding transformer has a dummy id (2) and dummy nodes (0 and 1).
    - The from status is the actual status of the threewinding transformer with teh corresponding node,
      the to status is always true.
    - The voltage at the dummy node is the same as on node 1
    - i0 and p0 are only applicable to T1
    - The WindingType at the side of the dummy_node is alway wye_n
    - The voltage levels will be calculated in advance, so tap_pos/min/max/nom/size can all be set to zero
    - uk and pk are calculated in advance, so uk_min/max and pk_min/max can be set to nan
    */
    std::tuple<TransformerInput, TransformerInput, TransformerInput> get_two_winding_transformer_inputs() const {
        // off nominal tap ratio
        auto const [u1, u2, u3] = [this]() {
            double u1 = u1_, u2 = u2_, u3 = u3_;
            if (tap_side_ == Branch3Side::side_1) {
                u1 += tap_direction_ * (tap_pos_ - tap_nom_) * tap_size_;
            }
            else if (tap_side_ == Branch3Side::side_2) {
                u2 += tap_direction_ * (tap_pos_ - tap_nom_) * tap_size_;
            }
            else {
                u3 += tap_direction_ * (tap_pos_ - tap_nom_) * tap_size_;
            }
            return std::make_tuple{u1, u2, u3};
        }();

        auto const [uk_T1, uk_T2, uk_T3] = calculate_uk();
        auto const [pk_T1, pk_T2, pk_T3] = calculate_pk();

        TransformerInput transformer_input_T1{
            {{2}, 0, 1, status_1(), true},  // {{id}, from_node, to_node, from_status, to_status}
            u1,                             // u1
            u1,                             // u2
            sn_1_,                          // sn
            uk_T1,                          // uk
            pk_T1,                          // pk
            i0_,                            // i0
            p0_,                            // p0
            winding_1_,                     // winding_from
            WindingType::wye_n,             // winding_to
            0,                              // clock
            BranchSide::from,               // tap_side
            0,                              // tap_pos
            0,                              // tap_min
            0,                              // tap_max
            0,                              // tap_nom
            0.0,                            // tap_size
            nan,                            // uk_min
            nan,                            // uk_max
            nan,                            // pk_min
            nan,                            // pk_max
            z_grounding_1_.real(),          // r_grounding_from
            z_grounding_1_.imag(),          // x_grounding_from
            0,                              // r_grounding_to
            0                               // x_grounding_to
        };
        TransformerInput transformer_input_T2{
            {{2}, 0, 1, status_2(), true},  // {{id}, from_node, to_node, from_status, to_status}
            u2,                             // u1
            u1,                             // u2
            sn_2_,                          // sn
            uk_T2,                          // uk
            pk_T2,                          // pk
            0.0,                            // i0
            0.0,                            // p0
            winding_2_,                     // winding_from
            WindingType::wye_n,             // winding_to
            clock_12_,                      // clock
            BranchSide::from,               // tap_side
            0,                              // tap_pos
            0,                              // tap_min
            0,                              // tap_max
            0,                              // tap_nom
            0.0,                            // tap_size
            nan,                            // uk_min
            nan,                            // uk_max
            nan,                            // pk_min
            nan,                            // pk_max
            z_grounding_2_.real(),          // r_grounding_from
            z_grounding_2_.imag(),          // x_grounding_from
            0,                              // r_grounding_to
            0                               // x_grounding_to
        };
        TransformerInput transformer_input_T3{
            {{2}, 0, 1, status_3(), true},  // {{id}, from_node, to_node, from_status, to_status}
            u3,                             // u1
            u1,                             // u2
            sn_3_,                          // sn
            uk_T3,                          // uk
            pk_T3,                          // pk
            0.0,                            // i0
            0.0,                            // p0
            winding_3_,                     // winding_from
            WindingType::wye_n,             // winding_to
            clock_13_,                      // clock
            BranchSide::from,               // tap_side
            0,                              // tap_pos
            0,                              // tap_min
            0,                              // tap_max
            0,                              // tap_nom
            0.0,                            // tap_size
            nan,                            // uk_min
            nan,                            // uk_max
            nan,                            // pk_min
            nan,                            // pk_max
            z_grounding_3_.real(),          // r_grounding_from
            z_grounding_3_.imag(),          // x_grounding_from
            0,                              // r_grounding_to
            0                               // x_grounding_to
        };
        return std::make_tuple(transformer_input_T1, transformer_input_T2, transformer_input_T3);
    }
};

}  // namespace power_grid_model

#endif